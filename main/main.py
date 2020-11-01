from delegate_emr import delegate_emr

def start(event, context):
	print(event)

	delegate_emr(event, context)