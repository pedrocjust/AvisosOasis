import discord
from discord.ext import commands
from discord import ui
from utils.database import save_ausencia
import os

# Canais do .env
CANAL_SOLICITAR_AUSENCIA = int(os.getenv("CANAL_SOLICITAR_AUSENCIA"))
CANAL_LOG_AUSENCIA = int(os.getenv("CANAL_LOG_AUSENCIA"))


# Modal de solicitar ausência
class AusenciaModal(ui.Modal, title="Solicitação de Ausência"):
    nome = ui.TextInput(label="Nome", placeholder="Digite seu nome...", required=True)
    cargo = ui.TextInput(
        label="Cargo", placeholder="Digite seu cargo...", required=True
    )
    user_id = ui.TextInput(label="ID", placeholder="Digite seu ID...", required=True)
    motivo = ui.TextInput(
        label="Motivo da Ausência",
        style=discord.TextStyle.paragraph,
        placeholder="Descreva o motivo...",
        required=True,
    )
    data_retorno = ui.TextInput(
        label="Data de Retorno", placeholder="Ex: 30/04/2025", required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Salvar no banco
        data = {
            "nome": self.nome.value,
            "cargo": self.cargo.value,
            "user_id": self.user_id.value,
            "motivo": self.motivo.value,
            "data_retorno": self.data_retorno.value,
            "status": "Pendente",
        }
        save_ausencia(data)

        # Criar embed bonito
        embed = discord.Embed(
            title="📋 Nova Solicitação de Ausência",
            description="",
            color=discord.Color.blue(),
        )

        embed.add_field(
            name="👤 Nome do Funcionário", value=f"`{self.nome.value}`", inline=False
        )
        embed.add_field(name="🏛️ Cargo", value=f"`{self.cargo.value}`", inline=False)
        embed.add_field(name="🆔 ID", value=f"`{self.user_id.value}`", inline=False)
        embed.add_field(
            name="📝 Motivo da Ausência", value=f"`{self.motivo.value}`", inline=False
        )
        embed.add_field(
            name="📅 Data de Retorno",
            value=f"`{self.data_retorno.value}`",
            inline=False,
        )

        embed.set_footer(
            text=f"🕓 Registro realizado em {interaction.created_at.strftime('%d/%m/%Y %H:%M')}."
        )

        canal_log = interaction.client.get_channel(CANAL_LOG_AUSENCIA)
        await canal_log.send(embed=embed)

        await interaction.response.send_message(
            "✅ Ausência registrada com sucesso!", ephemeral=True
        )


# Botão de solicitar ausência no canal
class AusenciaView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="SOLICITAR AUSÊNCIA", style=discord.ButtonStyle.primary, emoji="📝"
    )
    async def solicitar_ausencia(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(AusenciaModal())


# Cog principal
class AusenciaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(CANAL_SOLICITAR_AUSENCIA)
        if channel is not None:
            await channel.purge(limit=10)
            embed = discord.Embed(
                title="📋 Solicitação de Ausência",
                description="Clique no botão abaixo para solicitar uma ausência.",
                color=discord.Color.blue(),
            )
            await channel.send(embed=embed, view=AusenciaView())


# Setup para carregar o Cog
async def setup(bot):
    await bot.add_cog(AusenciaCog(bot))
