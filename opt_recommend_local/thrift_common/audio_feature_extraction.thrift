struct AudioFrameFeature {
    1:list<double> values,
}

struct AudioFeature {
    1:list<AudioFrameFeature> audio_frame_features,
}

service AudioFeatureExtraction {
    AudioFeature extract(1:i64 video_id, 2:string video_uri)
}
