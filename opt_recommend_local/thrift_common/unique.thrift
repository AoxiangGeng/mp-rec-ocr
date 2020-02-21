namespace py unique

struct addVideoRequest {
    1: string userId,
    2: string bucket,
    3: list<i64> videoIds,
}
struct addVideoResponse {
    1: i32 status,
}
struct getVideoRequest {
    1: string userId,
    2: string bucket,
    3: i32 count,
}
struct getVideoResponse {
     1: i32 status,
     2: list<i64> videoIds,
}
service UniqueService {
    addVideoResponse addVideo(1: addVideoRequest request),
    getVideoResponse getVideo(1: getVideoRequest request),
}
