import os
import sys
import logging

def script_init(maintainers,
                use_scribe=False, logging_file=True,
                script_name=None, logger_name=None, level=logging.INFO, rt_category=None, rt_thread_support=True,
                scribe_host='127.0.0.1', scribe_port=1464, databus_channel=None, databus_format=None,
                use_sentry=False, sentry_dsn=None, sentry_level=logging.ERROR):
    script_name = script_name or os.path.basename(sys.argv[0]).split(".")[0]

    import getpass
    username = getpass.getuser()
    if username in maintainers:
        testing = True
    else:
        testing = False

    log_filename = None
    if testing:
        log_filename = "/dev/stdout"
        use_scribe = False
    elif logging_file:
        log_filename = "/var/log/tiger/%s.log" % script_name

    if use_sentry:
        if sentry_dsn is None:
            sentry_dsn = os.getenv('SENTRY_DSN')
    else:
        sentry_dsn = None

    from pyutil.alarm.alarm_handler import AlarmHandler
    import pyutil.program.log as pyutil_log
    log_format ='%(asctime)s %(process)d %(levelname)s %(message)s'
    scribe_category = script_name if use_scribe else None
    pyutil_log.config_logging(
                              filename=log_filename,
                              category=scribe_category,
                              format=log_format,
                              level=level,
                              scribe_host=scribe_host,
                              scribe_port=scribe_port,
                              databus_channel=databus_channel,
                              databus_format=databus_format,
                              sentry_dsn=sentry_dsn,
                              sentry_level=sentry_level,
                             )
    if rt_category:
        pyutil_log.switch_rt_logging(rt_category=rt_category, thread_support=rt_thread_support)

    if testing:
        return


    logger = logging.getLogger(logger_name)

    # add MailHandler & set excepthook

    # This alarming is too annoying we have to find ways to
    #   disable it.
    # By xuruiqi
    if maintainers is None or \
            (type(maintainers) is list and len(maintainers) == 0):
        pass
    else:
        mail_users = ["%s@163.com" % u for u in maintainers]

        logger.addHandler(AlarmHandler(script_name, mail_users))

    def excepthook(t, v, tb):
        logging.error('Uncaught exception.', exc_info=(t, v, tb))

    sys.excepthook = excepthook

