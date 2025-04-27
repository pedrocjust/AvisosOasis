import discord
from discord.ext import commands
from discord import ui
from utils.database import save_demissao
import os

# Canais
CANAL_SOLICITAR_DEMISSAO = int(os.getenv("CANAL_SOLICITAR_DEMISSAO"))
CANAL_LOG_DEMISSAO = int(os.getenv("CANAL_LOG_DEMISSAO"))


# Modal para solicitar demissão
class DemissaoModal(ui.Modal, title="Solicitação de Demissão"):
    nome = ui.TextInput(label="Nome", placeholder="Digite seu nome...", required=True)
    cargo = ui.TextInput(
        label="Cargo", placeholder="Digite seu cargo...", required=True
    )
    motivo = ui.TextInput(
        label="Motivo da Demissão",
        style=discord.TextStyle.paragraph,
        placeholder="Descreva o motivo...",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        data = {
            "nome": self.nome.value,
            "cargo": self.cargo.value,
            "user_id": str(user_id),
            "motivo": self.motivo.value,
            "status": "Pendente",
        }
        save_demissao(data)

        embed = discord.Embed(
            title="📋 Nova Solicitação de Demissão", color=discord.Color.red()
        )
        embed.add_field(name="Nome", value=self.nome.value, inline=False)
        embed.add_field(name="Cargo", value=self.cargo.value, inline=False)
        embed.add_field(name="ID", value=str(user_id), inline=False)
        embed.add_field(name="Motivo", value=self.motivo.value, inline=False)
        embed.set_footer(text="Use os botões abaixo para aceitar ou recusar.")

        view = DemissaoLogView(user_id=user_id)

        log_channel = interaction.client.get_channel(CANAL_LOG_DEMISSAO)
        await log_channel.send(embed=embed, view=view)

        await interaction.response.send_message(
            "✅ Sua solicitação foi enviada com sucesso!", ephemeral=True
        )


# View do botão no canal de solicitação
class DemissaoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="SOLICITAR DEMISSÃO", style=discord.ButtonStyle.danger, emoji="📝")
    async def solicitar_demissao(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(DemissaoModal())


# View para aceitar ou recusar demissão no canal de logs
class DemissaoLogView(ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = int(user_id)

    @ui.button(label="✅ Aceitar Demissão", style=discord.ButtonStyle.success)
    async def aceitar_demissao(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = guild.get_member(self.user_id)

        if member is None:
            await interaction.followup.send(
                "❌ Usuário não encontrado no servidor.", ephemeral=True
            )
            return

        try:
            await member.edit(roles=[], nick=None)

            embed = interaction.message.embeds[0]
            cargo = interaction.user.top_role.name
            nome = interaction.user.display_name
            user_id = interaction.user.id

            # ➡️ Aqui adiciona um novo campo ao embed
            embed.add_field(
                name="✅ Demissão Aprovada",
                value=f"Aprovado por {nome} ",
                inline=False,
            )

            for child in self.children:
                child.disabled = True

            await interaction.message.edit(embed=embed, view=self)

            await interaction.followup.send(
                f"✅ Demissão de {member.mention} concluída e cargos removidos.",
                ephemeral=True,
            )

        except Exception as e:
            await interaction.followup.send(
                f"⚠️ Erro ao tentar remover cargos: `{e}`", ephemeral=True
            )

    @ui.button(label="❌ Recusar Demissão", style=discord.ButtonStyle.danger)
    async def recusar_demissao(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        embed = interaction.message.embeds[0]
        cargo = interaction.user.top_role.name
        nome = interaction.user.display_name
        user_id = interaction.user.id

        # ➡️ Adiciona um novo campo ao embed
        embed.add_field(
            name="❌ Demissão Recusada",
            value=f"Recusado por {nome}",
            inline=False,
        )

        for child in self.children:
            child.disabled = True

        await interaction.message.edit(embed=embed, view=self)

        await interaction.followup.send(
            "🚫 Solicitação de demissão foi recusada.", ephemeral=True
        )


# Cog principal
class DemissaoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(CANAL_SOLICITAR_DEMISSAO)
        if channel is not None:
            await channel.purge(limit=10)
            embed = discord.Embed(
                title="📋 Solicitação de Demissão",
                description="Clique no botão abaixo para solicitar sua demissão.",
                color=discord.Color.red(),
            )
            await channel.send(embed=embed, view=DemissaoView())


# Setup para carregar o Cog
async def setup(bot):
    await bot.add_cog(DemissaoCog(bot))
