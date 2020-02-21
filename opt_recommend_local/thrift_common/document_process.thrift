namespace cpp document_process
namespace py document_process

service DocumentProcessThrift{
    map<string, string> process(1:map<string, string> data)
}
