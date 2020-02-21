namespace cpp video_word2vec
namespace py video_word2vec
namespace go video_word2vec

struct ResInfo{
    1:list< list<double> > vec_list,
}

service VideoWord2Vec {
    // getter
    list<ResInfo> get_word2vec(1:list<string> req),
}
