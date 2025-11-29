from flask import Blueprint, jsonify

from sqlalchemy import func, and_, or_, case

from database import get_db

from models import Credenciado, Especialidade, CredenciadoEspecialidade



dashboard_bp = Blueprint('dashboard', __name__)



def _status_label_and_color(raw: str | None):

    if not raw:

        return ("Desconhecido", "#6b7280")

    s = raw.strip().lower()

    if s == 'ativo':

        return ("Ativo", "#10b981")

    if s in ('em análise', 'em analise', 'analise', 'analise pendente', 'em andamento'):

        return ("Em Análise", "#f59e0b")

    if s in ('inativo', 'desativado'):

        return ("Inativo", "#6b7280")

    if 'encerr' in s or 'fim' in s:

        return ("Contrato Encerrado", "#dc2626")

    

    return (raw, "#6b7280")



@dashboard_bp.route('/', methods=['GET'])

def get_dashboard():

    db = get_db()



    

    total = db.query(func.count(Credenciado.id)).scalar() or 0



    active = db.query(func.count(Credenciado.id)).filter(func.lower(Credenciado.status) == 'ativo').scalar() or 0

    under_review = db.query(func.count(Credenciado.id)).filter(

        or_(func.lower(Credenciado.status) == 'em análise', func.lower(Credenciado.status) == 'em analise')

    ).scalar() or 0

    strategic = db.query(func.count(Credenciado.id)).filter(Credenciado.parceiro_estrategico == True).scalar() or 0



    

    avg_appt = (

        db.query(func.avg(Credenciado.tempo_medio_agendamento))

        .filter(Credenciado.tempo_medio_agendamento.isnot(None))

        .filter(Credenciado.tempo_medio_agendamento > 0)

        .scalar()

    )

    avg_appt = float(avg_appt) if avg_appt is not None else 0.0



    

    coverage_rows = (

        db.query(Credenciado.cidade, Credenciado.estado, func.count(Credenciado.id))

        .group_by(Credenciado.cidade, Credenciado.estado)

        .order_by(func.count(Credenciado.id).desc())

        .limit(15)

        .all()

    )

    coverage = []

    for cidade, estado, count in coverage_rows:

        if not cidade and not estado:

            continue

        label = f"{cidade or ''} - {estado or ''}".strip().strip('-').strip()

        coverage.append({"region": label, "count": int(count or 0)})



    

    spec_rows = (

        db.query(Especialidade.descricao, func.count(CredenciadoEspecialidade.id))

        .join(CredenciadoEspecialidade, CredenciadoEspecialidade.id_especialidade == Especialidade.id)

        .group_by(Especialidade.descricao)

        .order_by(func.count(CredenciadoEspecialidade.id).desc())

        .all()

    )

    by_specialty = [

        {"specialty": (desc or "Sem descrição"), "count": int(count or 0)} for desc, count in spec_rows

    ]



    

    dist_rows = db.query(Credenciado.status, func.count(Credenciado.id)).group_by(Credenciado.status).all()

    status_distribution = []

    for raw, count in dist_rows:

        label, color = _status_label_and_color(raw)

        status_distribution.append({"status": label, "count": int(count or 0), "color": color})



    

    

    complexities_distinct = (

        db.query(func.count(func.distinct(Credenciado.complexidade)))

        .filter(Credenciado.complexidade.isnot(None))

        .filter(Credenciado.complexidade != '')

        .scalar()

        or 0

    )



    

    complexities_rows = (

        db.query(Credenciado.complexidade, func.count(Credenciado.id))

        .filter(Credenciado.complexidade.isnot(None))

        .filter(Credenciado.complexidade != '')

        .group_by(Credenciado.complexidade)

        .order_by(func.count(Credenciado.id).desc())

        .all()

    )

    complexities_distribution = [

        {"level": (lvl or "Sem informação"), "count": int(cnt or 0)} for lvl, cnt in complexities_rows

    ]



    stats = {

        "totalProviders": int(total),

        "activeProviders": int(active),

        "strategicPartners": int(strategic),

        "underReview": int(under_review),

        "averageAppointmentTime": avg_appt,

        "coverageByRegion": coverage,

        "providersBySpecialty": by_specialty,

        "statusDistribution": status_distribution,

        "complexitiesDistinct": int(complexities_distinct),

        "complexitiesDistribution": complexities_distribution,

    }



    

    

    nulls_last = case((Credenciado.ultima_atualizacao.is_(None), 1), else_=0)

    recent_items = (

        db.query(Credenciado)

        .order_by(nulls_last.asc(), Credenciado.ultima_atualizacao.desc(), Credenciado.id.desc())

        .limit(5)

        .all()

    )

    recent = []

    for c in recent_items:

        recent.append({

            "id": c.id,

            "nome": c.nome,

            "cidade": c.cidade,

            "estado": c.estado,

            "bairro": c.bairro,

            "tipo": c.tipo,

            "status": c.status,

            "parceiro_estrategico": c.parceiro_estrategico,

            "tempo_medio_agendamento": c.tempo_medio_agendamento,

            "ultima_atualizacao": c.ultima_atualizacao.isoformat() if c.ultima_atualizacao else None,

            "especialidades": [e.descricao for e in getattr(c, 'especialidades', [])],

        })



    return jsonify({

        "stats": stats,

        "recent": recent,

    })

