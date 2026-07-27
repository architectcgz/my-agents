# caarlos0/env v11

Use this reference when adding or reviewing `github.com/caarlos0/env/v11` configuration structs, tags, parser behavior, `Parse*` options, `OnSet`, or custom parsers.

This bundled reference was verified against `github.com/caarlos0/env/v11` `v11.4.1`. Before applying it, inspect the target repository's pinned version and treat that version's README and source as canonical; do not assume that an unpinned `main` branch or another v11 release has identical behavior.

## Official sources

| Source | Use |
| --- | --- |
| [README](https://github.com/caarlos0/env/blob/v11.4.1/README.md) | Supported types, tags, options, and examples |
| [Package documentation](https://pkg.go.dev/github.com/caarlos0/env/v11) | Exported API and runnable examples |
| [`env.go` parser source](https://github.com/caarlos0/env/blob/v11.4.1/env.go) | Exact built-in parser and option behavior |
| [`time.ParseDuration`](https://pkg.go.dev/time#ParseDuration) | Syntax accepted for `time.Duration` |
| [`strconv.ParseBool`](https://pkg.go.dev/strconv#ParseBool) | Syntax accepted for `bool` |
| [`encoding.TextUnmarshaler`](https://pkg.go.dev/encoding#TextUnmarshaler) | Extension point for a type-owned textual parser |

## Responsibility boundary

`env` loads values from the process environment (or an injected test map), applies defaults, and performs syntax/type conversion. It does not know service semantics such as:

- whether a parsed number must be positive or non-negative;
- whether two pool sizes are consistent;
- whether a URL uses the required scheme;
- whether an enum value is supported; or
- whether several fields form a valid combination.

Keep those rules in a single configuration validation step after parsing and before dependency wiring. Do not read environment variables from handlers, repositories, clients, domain code, or ordinary constructors.

## Built-in parsing behavior

The v11 implementation has built-in parsers for the ordinary scalar types and several common types. The important backend cases are:

| Go field type | Parsing behavior | Examples |
| --- | --- | --- |
| `string` | Keep the value as text | `"postgres://..."` |
| `bool` | Use `strconv.ParseBool` | `true`, `TRUE`, `1`, `t`, `false`, `0`, `f` |
| `int`, `int8` ... `int64` | Use base-10 integer parsing | `0`, `42`, `-1` |
| `time.Duration` | Use `time.ParseDuration` | `200ms`, `5s`, `1m30s` |
| `url.URL` | Use `url.Parse` | `https://example.com` |
| `encoding.TextUnmarshaler` | Call the type's `UnmarshalText` method | Domain-specific textual syntax |

Pointers, slices, maps, and combinations of supported types are also handled by the library. Check the pinned package documentation before relying on an uncommon nested shape.

### Duration values are native

`time.Duration` is a special built-in type, not an ordinary `int64` field. `env` calls `time.ParseDuration`, so a field can be declared directly:

```go
type HTTPEnvironment struct {
	ReadTimeout time.Duration `env:"READ_TIMEOUT" envDefault:"5s"`
}
```

`READ_TIMEOUT=5s` becomes `5 * time.Second`; `READ_TIMEOUT=200ms` becomes `200 * time.Millisecond`. A bare `5` is invalid because duration syntax requires a unit. The parser accepts the units and compound forms documented by [`time.ParseDuration`](https://pkg.go.dev/time#ParseDuration).

### Integer values are decimal integers

An `int64` field uses decimal integer parsing. It does not interpret human-readable size suffixes or duration suffixes:

```go
type HTTPEnvironment struct {
	MaxJSONBodyBytes int64 `env:"MAX_JSON_BODY_BYTES" envDefault:"1048576"`
}
```

```text
MAX_JSON_BODY_BYTES=1048576  # valid
MAX_JSON_BODY_BYTES=1MiB     # parse error
MAX_JSON_BODY_BYTES=1MB      # parse error
```

Put the unit in the environment variable name (`*_BYTES`, `*_SECONDS`, `*_MILLISECONDS`) when a numeric contract is intentional. If a contract must accept `1MiB` or another domain syntax, use an explicit parser (`FuncMap` or `encoding.TextUnmarshaler`) and test the conversion rules; do not expect `int64` parsing to provide them.

### Boolean values are parser-equivalent, not semantic policy

For a `bool` field, the library delegates to `strconv.ParseBool`. This accepts the documented true/false forms, including `1`/`0`, upper-case variants, and short forms such as `t`/`f`. If a service contract needs one canonical spelling, enforce that separately or use a string input plus explicit validation. Do not add a wrapper type merely to restate `ParseBool` behavior.

## Struct tags

The primary tags are:

- `env:"NAME"`: select the environment variable; options are comma-separated, for example `env:"DSN,required,notEmpty"`.
- `envDefault:"value"`: provide a default when the variable is absent (and, with the default options, when an optional variable is present but empty).
- `envPrefix:"PREFIX_"`: prepend a prefix to fields of a nested/complex struct.
- `envSeparator:";"`: change the separator used for slices and maps.
- `envKeyValSeparator:"="`: change the key/value separator used for maps.

The supported `env` options include:

- `required`: fail if the variable is not set;
- `notEmpty`: fail if the variable is set to an empty value;
- `file`: treat the value as a file path and load its contents;
- `expand`: expand environment references in the value;
- `init`: initialize nil pointers; and
- `unset`: unset the variable after reading it.

Keep required secrets explicit. Do not add an `envDefault` for passwords, tokens, private keys, production DSNs, or other credentials merely to make local startup easier.

## Parse entry points and options

The package provides `Parse`, `ParseAs`, `ParseWithOptions`, and `ParseAsWithOptions`. Use `ParseAsWithOptions` when tests need an injected environment map or when startup needs a deliberate parser option:

```go
parsed, err := env.ParseAsWithOptions[environment](env.Options{
	Environment: values,
})
if err != nil {
	return Config{}, err
}
```

Relevant `env.Options` fields are:

- `Environment`: replace `os.Environ()` with an explicit map; use this in tests instead of mutating global process state.
- `OnSet`: observe each assignment and whether it came from an explicit environment value or a default; keep callbacks side-effect-light and never log secrets.
- `FuncMap`: register a parser for a specific `reflect.Type` when the contract genuinely has custom textual syntax.
- `RequiredIfNoDef`: make fields without `envDefault` required.
- `Prefix`, `TagName`, `PrefixTagName`, and `DefaultValueTagName`: adjust naming only when the surrounding configuration contract requires it.

`env.Must` is available for panic-on-error startup code, but returning the error is normally clearer for libraries and tests. A process root may choose `Must` only when the startup policy explicitly treats invalid configuration as an unrecoverable boot failure.

## Recommended backend shape

Keep the environment DTO and runtime configuration separate. The DTO owns tags and syntax representation; the runtime config owns already-parsed ordinary Go values and has no environment concerns.

```go
type environment struct {
	HTTP struct {
		ReadTimeout time.Duration `env:"READ_TIMEOUT" envDefault:"5s"`
	} `envPrefix:"ZHICORE_CONTENT_HTTP_"`
	MaxJSONBodyBytes int64 `env:"ZHICORE_CONTENT_HTTP_MAX_JSON_BODY_BYTES" envDefault:"1048576"`
}

func load() (RuntimeConfig, error) {
	parsed, err := env.ParseAs[environment]()
	if err != nil { // syntax/type error at the configuration boundary
		return RuntimeConfig{}, err
	}
	cfg := toRuntimeConfig(parsed)
	if err := validate(cfg); err != nil { // semantic error before wiring
		return RuntimeConfig{}, err
	}
	return cfg, nil
}
```

Use ordinary Go types (`bool`, `int64`, `time.Duration`, `string`) unless a custom textual grammar is required. A named wrapper whose only purpose is positivity, non-negativity, enum checking, or `ParseBool` normalization obscures the boundary; perform those checks in `validate` instead.

## Failure modes and tests

Separate these failure classes in tests and error handling:

1. **Parse errors**: malformed syntax or an out-of-range scalar, such as `READ_TIMEOUT=soon`, `READ_TIMEOUT=5`, or `MAX_JSON_BODY_BYTES=1MiB` for the field types above.
2. **Semantic validation errors**: syntactically valid but unacceptable values, such as `READ_TIMEOUT=0s`, `MAX_JSON_BODY_BYTES=-1`, or an unsupported enum.
3. **Dependency/wiring errors**: valid configuration that cannot open a required external dependency.

Recommended focused coverage includes defaults, explicit overrides, required/not-empty fields, malformed values, zero/negative semantic values, `Environment` map isolation, and redacted configuration summaries. Do not weaken validation or change a field type merely to make a failing test pass.

## Gotchas

- Unexported struct fields are ignored by `env`; configuration fields must be exported.
- `envDefault` is syntax parsing, not business validation. A default of `0`, `0s`, or an empty string may still need to be rejected by the service validator.
- `required` and `notEmpty` are distinct: a missing variable and a present-but-empty variable are different failure cases.
- `envPrefix` changes the final key but does not move semantic ownership into the parser.
- `OnSet` receives values during parsing, including defaults; use its `isDefault` signal rather than guessing from the value.
- Do not silently accept old environment names unless backward compatibility is an explicit requirement; duplicate tags or ad-hoc fallback reads create two configuration contracts.
