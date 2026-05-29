# Type Composition

## Goal

Choose `extends`, intersection `&`, and union `|` based on schema semantics instead of style preference alone.

Use these rules when the user explicitly asks for richer TypeScript composition, or when the schema structure clearly benefits from it.

## Decision rules

### Use `extends`

Use `extends` when:

- the schema is object-shaped
- `allOf` has one clear base object
- the rest of the schema looks like additive extension fields

Example:

```ts
interface UserDetail extends UserBase {
  profile?: UserProfile;
}
```

### Use intersection `&`

Use `&` when:

- `allOf` combines multiple peer object fragments
- there is no obvious single base object
- the result is more naturally expressed as composition than inheritance

Example:

```ts
type UserDetail = UserBase & AuditFields & PermissionFields;
```

### Use union `|`

Use `|` when:

- the source schema is `oneOf`
- the source schema is `anyOf`
- the result is a literal enum union

Example:

```ts
type LoginResult = LoginSuccess | LoginError;
```

## Practical priority

1. Plain object -> prefer `interface`
2. `allOf` with one clear base object -> prefer `interface extends`
3. `allOf` with multiple peer fragments -> prefer `type A = B & C`
4. `oneOf` or `anyOf` -> prefer `type A = B | C`
5. If the user explicitly requires `type`, keep the output in `type` form even when `extends` would be possible

## Warnings

- Do not translate every `allOf` into `extends`
- `anyOf` to `|` is usually a practical approximation, not a perfect semantic match
- Prefer readable output over clever output
