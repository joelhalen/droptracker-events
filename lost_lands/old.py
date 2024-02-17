#
# @bot.command(
#     name="send_mass_dm",
#     description="sends team selection info to players",
#     default_member_permissions=interactions.Permissions.ADMINISTRATOR,
#     options=[
#         interactions.Option(
#             name="header",
#             description="Header text",
#             type=interactions.OptionType.STRING,
#             required=True
#         ),
#         interactions.Option(
#             name="first_text",
#             description="First line of text. \n signifies a new line.",
#             type=interactions.OptionType.STRING,
#             required=True
#         ),
#         interactions.Option(
#             name="bottom_text",
#             description="Bottom",
#             type=interactions.OptionType.STRING,
#             required=False
#         )
#     ]
# )
# async def send_mass_dm(ctx, header: str = "", first_text: str = "", bottom_text: str = ""):
#     target_message = await interactions.get(bot, interactions.Message, object_id=1161708840337809538,
#                                             parent_id=753996671494389820)
#     reacted_users = await target_message.get_users_from_reaction(emoji="\U0001F919")
#     target_guild = await interactions.get(bot, interactions.Guild, object_id=1131575888937504798)
#     guild_members = await target_guild.get_all_members()
#     print(f"Users that reacted: {reacted_users}")
#     for user in guild_members:
#         try:
#             await user.send(
#                 f"### False Alarm!\n> Sorry, I sent you the wrong link! Please use this one:\nhttps://discord.com/channels/1131575888937504798/1166165832469069904/1167271140708851794")
#         except:
#             continue
#         await asyncio.sleep(1)
#     await ctx.send("Done.", ephemeral=True)

#
# @create_task(IntervalTrigger(120))
# async def send_upkeepmsg():
#     upkeep_channel = await interactions.get(bot, interactions.Channel, object_id=1163291010768584764)
#     await upkeep_channel.purge(15)
#     await upkeep_channel.send("We are still online.")
