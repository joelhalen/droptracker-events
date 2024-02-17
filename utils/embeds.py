import interactions
from interactions import Embed, Message, User, Member, get, Interaction, MessageReaction


async def create_shop_embed(event_name, items):
    # embed = Embed(title="Lost Lands Items",
    #               color=0xff0000)
    embeds = []
    skip = False
    main_content = ("Your team can purchase items using points you earn from completing tasks.\n"
                    "> Learn more about **points**: https://events.droptracker.io/docs/ll/points\n"
                    "> Learn more about **items**: https://events.droptracker.io/docs/ll/items")
    for item in items:
        embed = Embed(title=item.full_name, description=item.description)
        embed.add_field(name="Value:", value=item.cost, inline=True)
        embed.add_field(name="Type:", value=item.type, inline=True)

        embed.add_field(name=item.full_name,
                        value="Type: " + item.type + "\n" +
                              item.description + "\nCost: `" +
                              str(item.price) + " gp`")
        embed.set_thumbnail(item.image_url)
        embed.set_footer(text="DropTracker Events | events.droptracker.io")
        if len(embeds) < 9:
            embeds.append(embed)
        else:
            message = interactions.Message(content=main_content,
                                           embeds=embeds)
            skip = True
            embeds = []
    if not skip:
        message = interactions.Message(content=main_content,
                                       embeds=embeds)
    else:
        message = interactions.Message(message="",
                                       embeds=embeds)
    return message

