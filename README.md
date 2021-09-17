#### Quick Example

```py
import discordsdk


client = discordsdk.Client()

# make a basic slash command

@client.slash_command(guild_ids=[00000000])
async def hello(ctx):
    await ctx.send("hello world!")


client.run("TOKEN")
```