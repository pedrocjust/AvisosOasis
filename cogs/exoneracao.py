import discord
from discord.ext import commands
from discord import ui
from utils.database import save_exoneracao
import os
from datetime import datetime

CANAL_CRIAR_EXONERACAO = int(os.getenv("CANAL_CRIAR_EXONERACAO"))
CANAL_EXONERACAO = int(os.getenv("CANAL_EXONERACAO"))


class ExoneracaoModal(ui.Modal, title="Exonerar Funcionário"):
    user_id = ui.TextInput(
        label="ID do Usuário",
        placeholder="Digite o ID do funcionário...",
        required=True,
    )
    nome = ui.TextInput(
        label="Nome do Usuário",
        placeholder="Digite o nome do funcionário...",
        required=True,
    )
    motivo = ui.TextInput(
        label="Motivo da Exoneração",
        style=discord.TextStyle.paragraph,
        placeholder="Explique o motivo...",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        resetado = False  # <-- inicializar aqui!

        try:
            membro = guild.get_member(int(self.user_id.value))

            if membro:
                await membro.edit(roles=[], nick=None)
                resetado = True
        except Exception as e:
            resetado = False
            print(f"Erro ao tentar exonerar: {e}")

        # Salvar no banco
        data = {
            "user_id": self.user_id.value,
            "nome": self.nome.value,
            "motivo": self.motivo.value,
        }
        save_exoneracao(data)

        # Criar embed lindo
        embed = discord.Embed(
            title="🚨 Funcionário Exonerado", description="", color=discord.Color.red()
        )

        embed.add_field(
            name="👤 Nome do Funcionário", value=f"`{self.nome.value}`", inline=False
        )
        embed.add_field(
            name="📄 Motivo da Exoneração", value=f"`{self.motivo.value}`", inline=False
        )

        if resetado:
            embed.add_field(
                name="✅",
                value="",
                inline=False,
            )
        else:
            embed.add_field(
                name="⚠️",
                value="",
                inline=False,
            )

        embed.set_footer(
            text=f"📌 Registro realizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}."
        )

        exoneracao_channel = interaction.client.get_channel(CANAL_EXONERACAO)
        await exoneracao_channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Exoneração registrada com sucesso!", ephemeral=True
        )


# View do botão "Exonerar Funcionário"
class ExoneracaoView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(
        label="EXONERAR FUNCIONÁRIO", style=discord.ButtonStyle.danger, emoji="⚡"
    )
    async def exonerar_funcionario(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(ExoneracaoModal())


# Cog da Exoneração
class ExoneracaoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(CANAL_CRIAR_EXONERACAO)
        if channel is not None:
            await channel.purge(limit=10)  # Limpa o canal para deixar só o botão
            embed = discord.Embed(
                title="🚨 Exonerar Funcionário",
                description="Clique no botão abaixo para exonerar um funcionário.",
                color=discord.Color.dark_red(),
            )
            await channel.send(embed=embed, view=ExoneracaoView())


# ESSA PARTE É MUITO IMPORTANTE PARA O BOT CARREGAR O COG:
async def setup(bot):
    await bot.add_cog(ExoneracaoCog(bot))
