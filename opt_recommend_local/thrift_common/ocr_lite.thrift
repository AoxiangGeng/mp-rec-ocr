namespace py ocr_lite_prediction

struct OcrPrediction{
    1: double degree;
    2: list<double> location;
    3: double width;
    4: double height;
    5: string text;
    6: double weight;
}

struct Req{
    1: string location;
}

struct Rsp{
    1: list<OcrPrediction> predictions;
    2: string videoLocation;
}

service Ocr_Lite_Prediction{
    Rsp get(1:Req req),
    list<Rsp> gets(1:list<Req> reqs),
}