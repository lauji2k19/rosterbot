def is_co():
    async def predicate(ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        co_role = get(ctx.guild.roles, name=local_settings['co_role_name'])
        if co_role in ctx.message.author.roles:
            return True
        else:
            raise customerrors.NotCOError
    return commands.check(predicate)

def is_roster_manager():
    async def predicate(ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        manager_role = get(ctx.guild.roles, name=local_settings['roster_manager_role_name'])
        co_role = get(ctx.guild.roles, name=local_settings['co_role_name'])
        if manager_role in ctx.message.author.roles or co_role in ctx.message.author.roles:
            return True
        else:
            raise customerrors.NotRosterManagerError
    return commands.check(predicate)

def economy_is_enabled():
    async def predicate(ctx):
        local_settings = settings.get_server_settings(ctx.guild.id)
        if local_settings['economy_table'] is not None:
            return True
        else:
            raise customerrors.EconomyNotEnabledError
    return commands.check(predicate)