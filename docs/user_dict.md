# Sudachi ユーザー辞書作成方法

### 使い方

```
$ sudachipy ubuild ja_entityparser/dict/legal_form.csv -s .venv/lib/python3.13/site-packages/sudachidict_core/resources/system.dic -o ja_entityparser/dict/ja-entity-parser.dic
```

### Memo
* ユーザ辞書にコメントを入れることはできない
* 空白行を入れることは問題ない

### Reference
[Sudachi ユーザー辞書作成方法 - WorksApplications/Sudachi](https://github.com/WorksApplications/Sudachi/blob/develop/docs/user_dict.md)
[紛らわしい記号総まとめ＋Rubyでどう変換されるかのメモ](https://qiita.com/YSRKEN/items/edb5bab23b7d92a3bf63)