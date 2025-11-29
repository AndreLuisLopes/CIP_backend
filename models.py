from sqlalchemy import (

    Column, Integer, String, Date, DateTime, Boolean, 

    DECIMAL, ForeignKey, Text

)

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from database import Base



class Login(Base):

    __tablename__ = "login"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    usuario = Column(Integer, nullable=False)

    senha = Column(String(255), nullable=False)

    cargo = Column(String(40), nullable=False)

    ultima_atualizacao = Column(Date, nullable=False)



class Credenciado(Base):

    __tablename__ = "credenciado"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    

    

    

    credenciamento = Column(String(50), index=True)

    nome = Column(String(150), nullable=False)

    crm = Column(String(20))

    telefone = Column(String(20))

    email = Column(String(150))

    status = Column(String(50))

    data_contrato = Column(Date)

    ultima_atualizacao = Column(DateTime, default=func.now(), onupdate=func.now())

    complexidade = Column(String(50))

    logradouro = Column(String(150))

    bairro = Column(String(100))

    numero = Column(String(10))

    cidade = Column(String(100))

    estado = Column(String(2))

    cep = Column(String(15))

    tipo = Column(String(50))

    latitude = Column(DECIMAL(10, 6))

    longitude = Column(DECIMAL(10, 6))

    parceiro_estrategico = Column(Boolean, default=False)

    tempo_medio_agendamento = Column(Integer)

    tempo_medio_procedimento = Column(Integer)

    

    

    especialidades = relationship(

        "Especialidade",

        secondary="credenciado_especialidade",

        back_populates="credenciados"

    )

    diferenciais = relationship(

        "Diferencial",

        secondary="credenciado_diferencial",

        back_populates="credenciados"

    )

    redes = relationship(

        "Rede",

        secondary="credenciado_rede",

        back_populates="credenciados"

    )

    

    complexidades = relationship(

        "CredenciadoComplexidade",

        back_populates="credenciado",

        cascade="all, delete-orphan"

    )



class Especialidade(Base):

    __tablename__ = "especialidade"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    descricao = Column(String(100), nullable=False)

    

    credenciados = relationship(

        "Credenciado",

        secondary="credenciado_especialidade",

        back_populates="especialidades"

    )



class Diferencial(Base):

    __tablename__ = "diferencial"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    descricao = Column(String(150), nullable=False)

    

    credenciados = relationship(

        "Credenciado",

        secondary="credenciado_diferencial",

        back_populates="diferenciais"

    )



class Rede(Base):

    __tablename__ = "rede"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    nome = Column(String(150), nullable=False)

    descricao = Column(Text)

    

    credenciados = relationship(

        "Credenciado",

        secondary="credenciado_rede",

        back_populates="redes"

    )



class Importacao(Base):

    __tablename__ = "importacao"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    descricao = Column(String(150))



class CredenciadoEspecialidade(Base):

    __tablename__ = "credenciado_especialidade"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_credenciado = Column(Integer, ForeignKey("credenciado.id", ondelete="CASCADE"))

    id_especialidade = Column(Integer, ForeignKey("especialidade.id", ondelete="CASCADE"))



class CredenciadoDiferencial(Base):

    __tablename__ = "credenciado_diferencial"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_credenciado = Column(Integer, ForeignKey("credenciado.id", ondelete="CASCADE"))

    id_diferencial = Column(Integer, ForeignKey("diferencial.id", ondelete="CASCADE"))



class CredenciadoRede(Base):

    __tablename__ = "credenciado_rede"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_credenciado = Column(Integer, ForeignKey("credenciado.id", ondelete="CASCADE"))

    id_rede = Column(Integer, ForeignKey("rede.id", ondelete="CASCADE"))



class CredenciadoComplexidade(Base):

    __tablename__ = "credenciado_complexidade"

    

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_credenciado = Column(Integer, ForeignKey("credenciado.id", ondelete="CASCADE"))

    id_especialidade = Column(Integer, ForeignKey("especialidade.id", ondelete="SET NULL"))

    id_credenciamento = Column(Integer)

    

    credenciado = relationship("Credenciado", back_populates="complexidades")

    especialidade = relationship("Especialidade")

