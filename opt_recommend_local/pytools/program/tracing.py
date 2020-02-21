#coding=utf-8
import opentracing
from opentracing import start_child_span

__all__ = ['init_tracer', 'start_tracer', 'start_span', 'start_child_span', 'get_current_span', 'opentracing']

noop_span = opentracing.Span(tracer=opentracing.tracer, context=opentracing.SpanContext())
def get_current_span():
    if hasattr(opentracing.tracer, 'get_current_span'):
        return opentracing.tracer.get_current_span()
    else:
        return noop_span

def get_current_trace_id():
    return getattr(get_current_span().context, 'trace_id', None)

def start_span(*args, **kwargs):
    return opentracing.tracer.start_span(*args, **kwargs)

def init_tracer():
    if hasattr(opentracing.tracer, 'init'):
        opentracing.tracer.init()

def start_tracer():
    if hasattr(opentracing.tracer, 'start'):
        opentracing.tracer.start()
