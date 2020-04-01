import os, signal, time, logging, multiprocessing

signal_names = {k: v for v, k in signal.__dict__.items() if v.startswith('SIG')}
def exit_signal_handler(sig=None, frame=None):
    # !!!WARNING
    # logging in a signal handler is strongly not recommended!
    # Because this may cause a deadlock
    #
    # I suggest you writing your own signal handler with `logging` eliminated
    logging.info('catch signal %s, exit ...', signal_names.get(sig, sig))

    while(multiprocessing.active_children()):
        for p in multiprocessing.active_children():
            p.terminate()
        time.sleep(.1)
    os._exit(0)
