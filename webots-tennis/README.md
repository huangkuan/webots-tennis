# Webots Tennis Court

This is a tiny Webots project containing a reusable standard tennis court `PROTO`.

## Files

- `protos/StandardTennisCourt.proto`: reusable regulation tennis court
- `worlds/tennis_court.wbt`: minimal world that instantiates the court

## Open In Webots

1. Open Webots.
2. Choose `File -> Open World...`
3. Open `worlds/tennis_court.wbt`

## Reuse In Another World

Add this near the top of your `.wbt` file:

```vrml
EXTERNPROTO "../protos/StandardTennisCourt.proto"
```

Then instantiate it:

```vrml
StandardTennisCourt {
  translation 0 0 0
}
```
