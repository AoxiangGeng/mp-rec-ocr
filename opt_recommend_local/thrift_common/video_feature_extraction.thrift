struct VideoFeature {
    1:list<string> video_frame_features,
}

service VideoFeatureExtraction {
    VideoFeature extract(1:i64 video_id, 2:string video_uri)
}
