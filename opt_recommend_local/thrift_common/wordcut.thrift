#!/usr/local/bin/thrift --gen cpp  --gen py --gen go

namespace cpp wordcut
namespace py wordcut
namespace go wordcut

service WordCut {
      // getter
      string get_words(1:string req),
      list<string> get_words_list(1:list<string> req),
      string get_words_with_weight(1:string req),
      list<string> get_words_with_weight_list(1:list<string> req),
      string get_words_accurate(1:string req, 2:string p),
      list<string> get_words_accurate_list(1:list<string> req, 2:string p),
}