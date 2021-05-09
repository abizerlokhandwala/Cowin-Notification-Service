import serverless_sdk
sdk = serverless_sdk.SDK(
    org_id='reziba',
    application_name='cowin-notification-service',
    app_uid='1mmmcGsgXWctlyP5cS',
    org_uid='da55c814-28e9-443d-aff0-49fee5a0b6cc',
    deployment_uid='fc8714bd-5a4f-4a2d-9253-a15bb42e12e7',
    service_name='cowin-notification-service',
    should_log_meta=True,
    should_compress_logs=True,
    disable_aws_spans=False,
    disable_http_spans=False,
    stage_name='dev',
    plugin_version='4.5.3',
    disable_frameworks_instrumentation=False,
    serverless_platform_stage='prod'
)
handler_wrapper_kwargs = {'function_name': 'cowin-notification-service-dev-unsubscribe', 'timeout': 30}
try:
    user_handler = serverless_sdk.get_user_handler('handler.unsubscribe')
    handler = sdk.handler(user_handler, **handler_wrapper_kwargs)
except Exception as error:
    e = error
    def error_handler(event, context):
        raise e
    handler = sdk.handler(error_handler, **handler_wrapper_kwargs)
