import os
import json

from todo.config import BASE_DIR


class Todo:
    """
    Todo模型类：操作数据
    """

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.content = kwargs.get('content', '')

    @classmethod
    def _db_path(cls):
        """获取存储todo数据文件的绝对路径"""
        # 返回 'todo_list/todo/db/todo.json' 文件的绝对路径
        path = os.path.join(BASE_DIR, 'db/todo.json')
        return path

    @classmethod
    def _load_db(cls):
        """加载 JSON 文件中所有todo数据"""
        path = cls._db_path()
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def _save_db(cls, data):
        """将todo数据保存到JSON文件"""
        path = cls._db_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def all(cls, sort=False, reverse=False):
        """获取全部todo"""
        # 这一步用来将所有从 JSON 文件中读取的todo数据转换为Todo实例化对象，方便后续操作
        todo_list = [cls(**todo_dict) for todo_dict in cls._load_db()]
        # 对数据按照 id 排序
        if sort:
            todo_list = sorted(todo_list, key=lambda x: x.id, reverse=reverse)
        return todo_list

    @classmethod
    def find_by(cls, limit=-1, ensure_one=False, sort=False, reverse=False, **kwargs):
        """查询todo"""
        result = []
        todo_list = [todo.__dict__ for todo in cls.all(sort=sort, reverse=reverse)]
        for todo in todo_list:
            # 根据关键字参数查询todo
            for k, v in kwargs.items():
                if todo.get(k) != v:
                    break
            else:
                result.append(cls(**todo))

        # 查询给定条数的数据
        if 0 < limit < len(result):
            result = result[:limit]
        # 查询结果集中的第一条数据
        if ensure_one:
            result = result[0] if len(result) > 0 else None

        return result

    @classmethod
    def get(cls, id):
        """通过id查询todo"""
        result = cls.find_by(id=id, ensure_one=True)
        return result

    def save(self):
        """保存todo"""
        # 查找出除self以外所有todo
        # todo.__dict__是保存了所有实例属性的字典
        todo_list = [todo.__dict__ for todo in self.all(sort=True) if todo.id != self.id]

        # 自增 id
        if self.id is None:
            # 如果 todo_list 长度大于 0 说明不是第一条todo，取最后一条todo的id加1
            if len(todo_list) > 0:
                self.id = todo_list[-1]['id'] + 1
            # 否则说明是第一条todo，id为 1
            else:
                self.id = 1

        # 将当前todo追加到todo_list
        todo_list.append(self.__dict__)
        # 将所有todo保存到文件
        self._save_db(todo_list)

    def delete(self):
        """删除todo"""
        todo_list = [todo.__dict__ for todo in self.all() if todo.id != self.id]
        self._save_db(todo_list)
