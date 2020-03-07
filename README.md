# Hyperlisp

A lisp of my own!

# Lexical grammar

```
NUM     /\-?([0-9]+\.[0-9]+|[1-9][0-9]*|0)/
ID      /[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/]/
STR     /"([^"\n\\]|\\[rbnv"\\])*"/
[       "["
]       "]"
(       "("
)       ")"
EOF     "\0"
```

# Syntax

```
entry ::= listy EOF
listy ::= (list | atom)+
list ::= "(" [listy] ")"
atom ::= ID | NUM | STR | "[" [listy] "]"
```

# Functionality (built-in)

* `(bind Identifier _)` variable binding
* `(func <Array|List|Identifier> ...)` anonymous function
