thrift_library(
    name = 'recommend_thrift',
    srcs = 'recommend.thrift',
)

thrift_library(
    name = 'profile_thrift',
    srcs = 'profile.thrift',
)

thrift_library(
    name = 'session_thrift',
    srcs = 'session.thrift',
)

thrift_library(
    name = 'pigsy_thrift',
    srcs = 'pigsy.thrift',
    deps = ':recommend_thrift',
)

thrift_library(
    name = 'lda_thrift',
    srcs = 'lda.thrift',
)

thrift_library(
    name = 'audio_feature_extraction_thrift',
    srcs = 'audio_feature_extraction.thrift',
)

thrift_library(
    name = 'document_process_thrift',
    srcs = 'document_process.thrift',
)
