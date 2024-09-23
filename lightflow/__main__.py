import argparse
import base64
import importlib
import json
import os
import requests
import yaml

from lightflow import IProto
from lightflow import get_proto_tasks as gpt


def serialize(args):

    sequence_files = [_f for _f in os.listdir(".") if _f.startswith("sequence") and _f.endswith(".yaml")]
    if not sequence_files:
        raise FileNotFoundError("In your current directory there are no sequence yaml file to be serialized")
    
    for sequence in sequence_files:
        with open(os.path.join(".", sequence), "r") as document:
            YAML = yaml.safe_load(document)

        IProto._IProto__PROTO_MODULE = YAML["__manifest__"]["module"]
        messages = []
        for pipeline in YAML["sequence"]:
            _p: dict = {pk: pv for pk, pv in pipeline.items() if not isinstance(pv, list)}
            _p_b, _p_t, _p_a = gpt(pipeline["before_pipeline"], pipeline["tasks"], pipeline["after_pipeline"])
            _p.update({"before_pipeline": _p_b, "tasks": _p_t, "after_pipeline": _p_a})
            messages.append(IProto("Pipeline", **_p))
        for ppl in messages:
            ppl_proto = ppl.proto
            encode_message = base64.urlsafe_b64encode(ppl.serialize()).decode("utf-8")
        print(encode_message)

def deserialize(args):

    recv_msg = importlib.import_module(args.proto_module).Pipeline()
    recv_msg.ParseFromString(base64.urlsafe_b64decode(args.message))
    print(recv_msg.name)

def main():
    parser = argparse.ArgumentParser(description="Command line application for command sequence")
    subparsers = parser.add_subparsers(dest='command', required=True)
        
    # Subparser for serialize
    parser_serialize = subparsers.add_parser('serialize', help="Serialize arguments to PROTO message")
    parser_serialize.set_defaults(func=serialize)

    # Subparser for deserialize
    parser_deserialize = subparsers.add_parser('deserialize', help="Deserialize PROTO message")
    parser_deserialize.add_argument(
        '--message', 
            type=str, 
            required=True, 
            help="Serialized message data"
        )
    parser_deserialize.add_argument(
        '--proto-module', 
            type=str, 
            required=True, 
            help="Protobuf module to use for parsing"
        )
    parser_deserialize.set_defaults(func=deserialize)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
