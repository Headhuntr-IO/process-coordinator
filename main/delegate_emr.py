import boto3
import uuid

from shared import env


def delegate_emr(event, context):
    print('EMR')

    job = event['job']
    cluster_name = env('EMR_CLUSTER_NAME')
    this_function_name = env('THIS_FUNCTION_NAME')

    if 'jar' in event:
        jar_data_proc = event['jar']
    else:
        jar_data_proc = env('JAR_DATA_PROCESSOR')

    if 'data_location' in event:
        data_location = event['data_location']
    else:
        data_location = 'default'

    random_id = uuid.uuid1()
    s3_data = env('S3_BUCKET_DATA_PROCESSOR')
    es_host = env('ES_HOST')

    jar_es_hadoop = env('JAR_ES_HADOOP')
    worker_sg = env('WORKER_SG')
    worker_subnet = env('WORKER_SUBNET')
    worker_instance_type = env('EMR_WORKER_INSTANCE_TYPE')
    worker_instance_count = int(env('EMR_WORKER_INSTANCE_COUNT'))

    emr = boto3.client('emr')
    lambda_client = boto3.client('lambda')

    step_name = job
    step_args = [
        'spark-submit',
        '--deploy-mode',
        'cluster',
        '--class',
        'io.headhuntr.JobRunner',
        '--jars',
        jar_data_proc,
        jar_es_hadoop,
        '--job', job,
        '--esHost', 'https://{es}:443'.format(es=es_host),
        '--dmzDir', 's3://{s3}/temp/{data_location}'.format(s3=s3_data, data_location=data_location),
        '--workingDir', 's3://{s3}/temp/emr/{id}/workspace'.format(s3=s3_data, id=random_id)
    ]

    if job == 'generic':
        file = event['file']
        index = event['index']

        generic_job_params = [
            '--file', file,
            '--index', index
        ]
        step_args.extend(generic_job_params)
        step_name = 'generic: {file} -> {index}'.format(file=file, index=index)

    step = {
        'Name': '{step_name} on {data_location}'.format(step_name=step_name, data_location=data_location),
        'ActionOnFailure': 'CONTINUE',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': step_args
        }
    }

    list_cluster_response = emr.list_clusters(ClusterStates=['STARTING', 'BOOTSTRAPPING', 'RUNNING', 'WAITING'])
    active_clusters = [cluster for cluster in list_cluster_response['Clusters'] if cluster['Name'] == cluster_name]
    if active_clusters:
        cluster_id = active_clusters[0]['Id']
        return emr.add_job_flow_steps(JobFlowId=cluster_id, Steps=[step])

    # use the event object
    my_tags = lambda_client.get_function(FunctionName=this_function_name)['Tags']
    tags = [{'Key': 'hh:emr-cost', 'Value': str(random_id)}]
    for key, value in my_tags.items():
        tags.append({'Key': key, 'Value': value})

    return emr.run_job_flow(
        Name=cluster_name,
        Applications=[{
            'Name': 'Spark'
        }],
        LogUri='s3://{s3}/temp/emr/{id}/logs'.format(s3=s3_data, id=random_id),
        ReleaseLabel='emr-5.30.1',
        Instances={
            'Ec2SubnetIds': [worker_subnet],
            'AdditionalSlaveSecurityGroups': [worker_sg],
            'AdditionalMasterSecurityGroups': [worker_sg],
            'InstanceGroups': [
                {
                    'Name': "Controller",
                    'Market': 'SPOT',
                    'InstanceRole': 'MASTER',
                    'InstanceType': worker_instance_type,
                    'InstanceCount': 1,
                },
                {
                    'Name': "Workers",
                    'Market': 'SPOT',
                    'InstanceRole': 'CORE',
                    'InstanceType': worker_instance_type,
                    'InstanceCount': worker_instance_count,
                }
            ]
        },
        Steps=[step],
        VisibleToAllUsers=True,
        ServiceRole='EMR_DefaultRole',
        JobFlowRole='EMR_EC2_DefaultRole',
        Tags=tags
    )
