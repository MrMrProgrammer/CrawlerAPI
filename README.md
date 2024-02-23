### Run Uvicorn Server :
```markdown
uvicorn main:app --reload
```
---
### Body Structure :
```markdown
{
    "urls" : ["https://www.tabnak.ir"],

    "fields" : [{
            "name" : "ali",
            "multi" : "False",
            "file" : "False",
            "ext_type" : "CLASS_NAME",
            "ext_value" : "title_main"
        },
        {
            "name" : "ali",
            "multi" : "False",
            "file" : "False",
            "ext_type" : "CLASS_NAME",
            "ext_value" : "title_main"
        }]
}
```

### ext_type :
```markdown
CLASS_NAME
```

```markdown
XPATH
```

```markdown
TAG_NAME
```

```markdown
CSS_SELECTOR
```

```markdown
ID
```

```markdown
LINK_TEXT ( #no now !)
```

```markdown
NAME ( #no now !)
```

----
```markdown
get_attribute()
```
