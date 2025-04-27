import discord
from discord.ext import commands
from discord import app_commands
from utils.database import get_ausencias


class ComandosCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="checarausencias", description="Lista todos os usuários em ausência."
    )
    async def checar_ausencias(self, interaction: discord.Interaction):
        ausencias = get_ausencias()

        if not ausencias:
            await interaction.response.send_message(
                "✅ Nenhuma ausência registrada no momento.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📋 Lista de Ausências",
            description="Ausências registradas atualmente:",
            color=discord.Color.blue(),
        )

        for ausencia in ausencias:
            nome = ausencia.get("nome", "Desconhecido")
            data_solicitacao = ausencia.get("data_solicitacao", "Data não registrada")[
                :10
            ]
            data_retorno = ausencia.get("data_retorno", "Data não informada")
            embed.add_field(
                name=f"👤 {nome}",
                value=f"**Solicitado em:** {data_solicitacao}\n**Retorno previsto:** {data_retorno}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ComandosCog(bot))
