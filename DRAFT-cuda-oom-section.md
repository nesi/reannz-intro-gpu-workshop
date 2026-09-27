# Orphaned from 04-how-much-memory.md

Removed when chapter 4 was narrowed to `--mem` only. This is VRAM content, so it
belongs in chapter 2's "GPU Memory" section. Not yet placed anywhere.

---

## Running out of GPU memory

The error is worth learning to read, because the useful part is not the part
people look at:

```
CUDA out of memory. Tried to allocate 64.00 MiB (GPU 0; 23034 MiB total
capacity; 22050 MiB already allocated; 512 MiB free).
```

| Phrase | Means |
|---|---|
| `Tried to allocate` | The allocation that failed — often small |
| `total capacity` | What the card has |
| `already allocated` | What **your process** was holding |
| `free` | What was left |

!!! note "The failed allocation is usually small"

    People see "Tried to allocate 64 MiB" and assume something strange has
    happened, because 64 MiB is nothing. The card was already 96% full; 64 MiB
    was the straw. **The number that matters is `already allocated`.**

What to do, in order:

1. **Reduce the batch size.** This is the whole fix most of the time. Halving
   the batch roughly halves activation memory and usually costs very little.
2. **Use a lower precision**, if the work tolerates it — fp32 → fp16 halves
   memory. [Chapter 8](08-precision.md) is about when that is safe.
3. **Check for a leak.** If usage climbs steadily across a long run rather than
   settling, you are holding on to something you meant to discard.
4. **Ask for a GPU with more VRAM.** Real, but last: bigger cards are scarcer
   and you will wait longer for one.
