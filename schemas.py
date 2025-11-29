from pydantic import BaseModel, EmailStr, Field

from typing import Optional, List

from datetime import date, datetime

from decimal import Decimal





class LoginRequest(BaseModel):

    usuario: int

    senha: str



class LoginResponse(BaseModel):

    access_token: str

    token_type: str

    cargo: str



class UserCreate(BaseModel):

    usuario: int

    senha: str

    cargo: str





class CredenciadoBase(BaseModel):

    nome: str

    crm: Optional[str] = None

    telefone: Optional[str] = None

    email: Optional[EmailStr] = None

    status: Optional[str] = None

    data_contrato: Optional[date] = None

    complexidade: Optional[str] = None

    logradouro: Optional[str] = None

    bairro: Optional[str] = None

    numero: Optional[str] = None

    cidade: Optional[str] = None

    estado: Optional[str] = None

    cep: Optional[str] = None

    tipo: Optional[str] = None

    latitude: Optional[Decimal] = None

    longitude: Optional[Decimal] = None

    parceiro_estrategico: bool = False

    tempo_medio_agendamento: Optional[int] = None

    tempo_medio_procedimento: Optional[int] = None



class CredenciadoCreate(CredenciadoBase):

    especialidades_ids: Optional[List[int]] = []

    diferenciais_ids: Optional[List[int]] = []

    redes_ids: Optional[List[int]] = []



class CredenciadoUpdate(BaseModel):

    nome: Optional[str] = None

    crm: Optional[str] = None

    telefone: Optional[str] = None

    email: Optional[EmailStr] = None

    status: Optional[str] = None

    data_contrato: Optional[date] = None

    complexidade: Optional[str] = None

    logradouro: Optional[str] = None

    bairro: Optional[str] = None

    numero: Optional[str] = None

    cidade: Optional[str] = None

    estado: Optional[str] = None

    cep: Optional[str] = None

    tipo: Optional[str] = None

    latitude: Optional[Decimal] = None

    longitude: Optional[Decimal] = None

    parceiro_estrategico: Optional[bool] = None

    tempo_medio_agendamento: Optional[int] = None

    tempo_medio_procedimento: Optional[int] = None

    especialidades_ids: Optional[List[int]] = None

    diferenciais_ids: Optional[List[int]] = None

    redes_ids: Optional[List[int]] = None



class CredenciadoResponse(CredenciadoBase):

    id: int

    ultima_atualizacao: datetime

    especialidades: List['EspecialidadeResponse'] = []

    diferenciais: List['DiferencialResponse'] = []

    redes: List['RedeResponse'] = []

    

    class Config:

        from_attributes = True





class EspecialidadeBase(BaseModel):

    descricao: str



class EspecialidadeCreate(EspecialidadeBase):

    pass



class EspecialidadeUpdate(BaseModel):

    descricao: Optional[str] = None



class EspecialidadeResponse(EspecialidadeBase):

    id: int

    

    class Config:

        from_attributes = True





class DiferencialBase(BaseModel):

    descricao: str



class DiferencialCreate(DiferencialBase):

    pass



class DiferencialUpdate(BaseModel):

    descricao: Optional[str] = None



class DiferencialResponse(DiferencialBase):

    id: int

    

    class Config:

        from_attributes = True





class RedeBase(BaseModel):

    nome: str

    descricao: Optional[str] = None



class RedeCreate(RedeBase):

    pass



class RedeUpdate(BaseModel):

    nome: Optional[str] = None

    descricao: Optional[str] = None



class RedeResponse(RedeBase):

    id: int

    

    class Config:

        from_attributes = True





class ImportacaoBase(BaseModel):

    descricao: Optional[str] = None



class ImportacaoCreate(ImportacaoBase):

    pass



class ImportacaoResponse(ImportacaoBase):

    id: int

    

    class Config:

        from_attributes = True





CredenciadoResponse.model_rebuild()

