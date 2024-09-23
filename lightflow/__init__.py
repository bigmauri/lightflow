import importlib

from datetime import datetime


class IProto:

	__PROTO_MODULE = None

	def __init__(self, _object, **kwargs):
		ts = datetime.now().timestamp()
		self._proto = getattr(importlib.import_module(self.__PROTO_MODULE), _object)()
		self._proto.id = f"{_object.lower()}-{str(ts).replace('.', '-')}"
		self._proto.timestamp = int(ts)
		for k, v in kwargs.items():
			if isinstance(v, list):
				getattr(self._proto, k).extend(v)
			elif isinstance(v, tuple):
				_, _enum = v
				setattr(self._proto, k, getattr(self._proto, _enum))
			elif k == "command":
				self._proto.command.CopyFrom(v)
			else:
				setattr(self._proto, k, v)

	@property
	def proto(self):
		return self._proto

	def serialize(self):
		return self._proto.SerializeToString()

def get_proto_commands(l: list):
	return [IProto("Command", **c).proto for c in l]

def get_proto_tasks(*l: list):
	proto_tasks = []
	for _ in l:
		_t_list = []
		for task in _:
			_t: dict = {tk: tv for tk, tv in task.items() if not isinstance(tv, list) and tk != "command"}
			_t_b, _t_c, _t_a = get_proto_commands(task["before_task"]), IProto("Command", **task["command"]).proto, get_proto_commands(task["after_task"])
			_t.update({"before_task": _t_b, "command": _t_c, "after_task": _t_a})
			_t_list.append(IProto("Task", **_t).proto)
		proto_tasks.append(_t_list)
	return proto_tasks
