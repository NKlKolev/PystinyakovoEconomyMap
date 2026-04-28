import json
import os
import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates


# -----------------------------
# Settings
# -----------------------------
DISPLAY_WIDTH = 1100


# -----------------------------
# Load region data
# -----------------------------
def load_regions():
    with open("regions.json", "r", encoding="utf-8") as file:
        return json.load(file)
def load_country():
    with open("country.json", "r", encoding="utf-8") as file:
        return json.load(file)


def save_country(country):
    with open("country.json", "w", encoding="utf-8") as file:
        json.dump(country, file, ensure_ascii=False, indent=2)

def update_derived_country_values(country):
    country["deficit"] = country.get("annual_spending", 0) - country.get("annual_revenue", 0)

    gdp = country.get("gdp", 0)
    public_debt = country.get("public_debt", 0)

    if gdp > 0:
        country["debt_to_gdp"] = round((public_debt / gdp) * 100, 1)
    else:
        country["debt_to_gdp"] = 0

    return country

def load_decisions_log():
    if not os.path.exists("decisions_log.json"):
        with open("decisions_log.json", "w", encoding="utf-8") as file:
            json.dump([], file, ensure_ascii=False, indent=2)

    with open("decisions_log.json", "r", encoding="utf-8") as file:
        return json.load(file)


def save_decisions_log(decisions_log):
    with open("decisions_log.json", "w", encoding="utf-8") as file:
        json.dump(decisions_log, file, ensure_ascii=False, indent=2)
# -----------------------------
# Save region data
# -----------------------------
def save_regions(regions):
    with open("regions.json", "w", encoding="utf-8") as file:
        json.dump(regions, file, ensure_ascii=False, indent=2)


# -----------------------------
# Find clicked region
# -----------------------------
def find_region_by_click(x, y, regions):
    for region in regions:
        x_min, x_max = region["x_range"]
        y_min, y_max = region["y_range"]

        if x_min <= x <= x_max and y_min <= y <= y_max:
            return region

    return None

INDICATOR_LABELS = {
    "economy": "Икономика",
    "education": "Образование",
    "urbanization": "Урбанизация",
    "fiscal_capacity": "Фискален капацитет",
    "state_dependency": "Зависимост от централната държава",
    "infrastructure": "Инфраструктура",
    "public_services": "Обществени услуги",
    "industrial_output": "Индустриално производство",
    "unemployment": "Безработица",
    "unrest": "Обществено напрежение",
    "corruption": "Корупция",
    "turnout": "Избирателна активност",
    "political_volatility": "Политическа волатилност",
    "traditionalism": "Традиционализъм",
    "progressivism": "Прогресивизъм",
    "regime_trust": "Доверие в режима",
    "opposition_strength": "Сила на опозицията",
    "patronage": "Патронаж",
    "local_identity": "Местна идентичност",
    "muslim_share": "Мюсюлманско население"
}

FISCAL_ACTIONS = {
    "tax_increase": "Данъчно увеличение",
    "spending_cuts": "Съкращаване на публични разходи",
    "debt_issue": "Емисия държавен дълг",
    "emergency_transfer": "Прехвърляне от аварийния резерв",
    "anti_corruption_recovery": "Антикорупционно възстановяване на средства",
    "privatization": "Приватизация / концесия",
    "state_enterprise_dividend": "Извънреден дивидент от държавни предприятия",
    "regional_levy": "Извънредна регионална вноска към централния бюджет"
}

# -----------------------------
# Policy Templates
# -----------------------------
POLICY_TEMPLATES = {
    "infrastructure_investment": {
        "label": "Инфраструктурна инвестиция",
        "description": "Подобрява инфраструктурата, стимулира икономиката и леко намалява безработицата, но носи риск от корупция при обществени поръчки.",
        "regional_effects": {
            "infrastructure": 8,
            "economy": 3,
            "unemployment": -2,
            "corruption": 1,
            "regime_trust": 2
        },
        "country_effects": {
            "political_capital": -1,
            "government_legitimacy": 1
        }
    },
    "employment_program": {
        "label": "Програма за заетост",
        "description": "Намалява безработицата и общественото напрежение, като подобрява икономическата активност и доверието в управлението.",
        "regional_effects": {
            "unemployment": -5,
            "economy": 2,
            "public_services": 1,
            "unrest": -3,
            "regime_trust": 3
        },
        "country_effects": {
            "government_legitimacy": 1
        }
    },
    "anti_corruption_reform": {
        "label": "Антикорупционна реформа",
        "description": "Намалява корупцията и патронажа, но струва политически капитал и може да създаде напрежение в зависими от клиентелистки мрежи области.",
        "regional_effects": {
            "corruption": -8,
            "patronage": -5,
            "regime_trust": 4,
            "unrest": 2
        },
        "country_effects": {
            "political_capital": -5,
            "government_legitimacy": 3,
            "national_stability": 1
        }
    },
    "social_program": {
        "label": "Социална програма",
        "description": "Подобрява обществените услуги и намалява напрежението, особено в зависими от държавата области.",
        "regional_effects": {
            "public_services": 6,
            "unrest": -4,
            "regime_trust": 3,
            "state_dependency": 2
        },
        "country_effects": {
            "government_legitimacy": 2,
            "political_capital": -1
        }
    },
    "industrial_subsidy": {
        "label": "Индустриална субсидия",
        "description": "Подкрепя производството и заетостта, но увеличава риска от патронаж и корупционно разпределение на ресурси.",
        "regional_effects": {
            "industrial_output": 7,
            "economy": 3,
            "unemployment": -2,
            "corruption": 2,
            "patronage": 2,
            "regime_trust": 2
        },
        "country_effects": {
            "political_capital": -2,
            "government_legitimacy": 1
        }
    },
    "security_measure": {
        "label": "Извънредна мярка за сигурност",
        "description": "Бързо намалява напрежението, но може да понижи легитимността и да засили опозицията, ако се възприеме като репресивна мярка.",
        "regional_effects": {
            "unrest": -8,
            "regime_trust": -2,
            "opposition_strength": 3,
            "corruption": 1
        },
        "country_effects": {
            "political_capital": -3,
            "government_legitimacy": -2,
            "national_stability": 1
        }
    }
}

def get_active_events(region):
    active_events = []

    economy = region.get("economy", 0)
    unemployment = region.get("unemployment", 0)
    unrest = region.get("unrest", 0)
    opposition_strength = region.get("opposition_strength", 0)
    regime_trust = region.get("regime_trust", 0)
    public_services = region.get("public_services", 0)
    corruption = region.get("corruption", 0)
    patronage = region.get("patronage", 0)

    if economy < 35 and unemployment > 25:
        active_events.append({
            "level": "🔴",
            "title": "Регионална икономическа криза",
            "reason": "Икономиката е слаба, а безработицата е висока. Това създава риск от обедняване, миграция и антиправителствено недоволство."
        })

    if unrest > 65 and opposition_strength > 60:
        active_events.append({
            "level": "🔴",
            "title": "Масови протести",
            "reason": "Общественото напрежение е високо, а опозицията има достатъчно сила да организира недоволството."
        })

    if public_services < 30:
        active_events.append({
            "level": "🟠",
            "title": "Криза в обществените услуги",
            "reason": "Обществените услуги са под критично ниво. Това може да засегне администрацията, здравеопазването, образованието и социалната подкрепа."
        })

    if corruption > 75 and regime_trust < 45:
        active_events.append({
            "level": "🟠",
            "title": "Корупционен скандал",
            "reason": "Корупцията е висока, а доверието в режима е ниско. Това прави злоупотребите политически видими и трудни за овладяване."
        })

    if patronage > 75 and corruption > 65 and regime_trust > 55:
        active_events.append({
            "level": "🟡",
            "title": "Патронажно овладяна област",
            "reason": "Областта изглежда стабилна, но тази стабилност се крепи върху зависимости, клиентелизъм и корупционни мрежи."
        })

    return active_events


def get_national_active_events(country):
    active_events = []

    treasury_balance = country.get("treasury_balance", 0)
    debt_to_gdp = country.get("debt_to_gdp", 0)
    inflation = country.get("inflation", 0)
    political_capital = country.get("political_capital", 0)
    national_stability = country.get("national_stability", 0)
    government_legitimacy = country.get("government_legitimacy", 0)
    emergency_reserve = country.get("emergency_reserve", 0)

    if treasury_balance < 200:
        active_events.append({
            "level": "🔴",
            "title": "Бюджетна криза",
            "reason": "Свободният фискален ресурс е критично нисък. Правителството има ограничена способност да финансира нови политики без дълг, данъци или съкращения."
        })

    if inflation > 10:
        active_events.append({
            "level": "🟠",
            "title": "Инфлационен натиск",
            "reason": "Инфлацията е над стабилното равнище. Това увеличава цените, намалява покупателната способност и може да засили общественото напрежение."
        })

    if debt_to_gdp > 80:
        active_events.append({
            "level": "🔴",
            "title": "Дългова уязвимост",
            "reason": "Държавният дълг е много висок спрямо размера на икономиката. Ново дългово финансиране може да повиши лихвите, дефицита и риска от фискална нестабилност."
        })

    if political_capital < 25:
        active_events.append({
            "level": "🔴",
            "title": "Политическа парализа",
            "reason": "Политическият капитал е критично нисък. Управляващите трудно могат да прокарват непопулярни реформи, бюджетни мерки или кризисни решения."
        })

    if government_legitimacy < 30:
        active_events.append({
            "level": "🔴",
            "title": "Криза на легитимността",
            "reason": "Легитимността на управлението е ниска. Решенията на централната власт могат да бъдат посрещнати с недоверие, съпротива или протести."
        })

    if national_stability < 35:
        active_events.append({
            "level": "🟠",
            "title": "Национална нестабилност",
            "reason": "Общата стабилност на държавата е отслабена. Регионални кризи, икономически натиск или политически конфликти могат по-лесно да се разширят."
        })

    if emergency_reserve < 100:
        active_events.append({
            "level": "🟠",
            "title": "Изчерпан аварийен резерв",
            "reason": "Аварийният резерв е почти изчерпан. Държавата е уязвима при природни бедствия, енергийни кризи, срив на обществени услуги или внезапни регионални сътресения."
        })

    return active_events


def clamp(value, min_value=0, max_value=100):
    return max(min_value, min(max_value, value))
def format_indicator(label, value, suffix="/100", higher_is_bad=False):
    if higher_is_bad:
        if value >= 75:
            icon = "🔴"
        elif value >= 55:
            icon = "🟠"
        elif value >= 35:
            icon = "🟡"
        else:
            icon = "🟢"
    else:
        if value <= 25:
            icon = "🔴"
        elif value <= 45:
            icon = "🟠"
        elif value <= 65:
            icon = "🟡"
        else:
            icon = "🟢"

    return f"**{icon} {label}:** {value}{suffix}"

# Streamlit app
# -----------------------------
st.set_page_config(
    page_title="Политико-икономическа карта на Пустиняково",
    layout="wide"
)

st.title("Политико-икономическа карта на Пустиняково")

regions = load_regions()
country = load_country()
decisions_log = load_decisions_log()

st.subheader("Национално състояние")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Свободен фискален ресурс", f"{country.get('treasury_balance', 0):,} млн.")
    st.metric("БВП", f"{country.get('gdp', 0):,} млн.")
    st.metric("Аварийен резерв", f"{country.get('emergency_reserve', 0):,} млн.")

with col2:
    st.metric("Годишни приходи", f"{country.get('annual_revenue', 0):,} млн.")
    st.metric("Годишни разходи", f"{country.get('annual_spending', 0):,} млн.")
    st.metric("Дефицит", f"{country.get('deficit', 0):,} млн.")

with col3:
    st.metric("Държавен дълг", f"{country.get('public_debt', 0):,} млн.")
    st.metric("Дълг към БВП", f"{country.get('debt_to_gdp', 0)}%")
    st.metric("Инфлация", f"{country.get('inflation', 0)}%")

with col4:
    st.metric("Данъчна тежест", f"{country.get('tax_burden', 0)}%")
    st.metric("Политически капитал", f"{country.get('political_capital', 0)}/100")
    st.metric("Национална стабилност", f"{country.get('national_stability', 0)}/100")
    st.metric("Легитимност", f"{country.get('government_legitimacy', 0)}/100")

national_active_events = get_national_active_events(country)

with st.container(border=True):
    st.subheader("Национални активни събития")

    if national_active_events:
        for event in national_active_events:
            st.markdown(f"**{event['level']} {event['title']}**")
            st.caption(event["reason"])
    else:
        st.success("Няма активни национални събития.")

info_left, info_right = st.columns([3, 1])

with info_right:
    if st.button("ℹ️ Как работи икономиката?"):
        st.session_state["show_economy_info"] = not st.session_state.get("show_economy_info", False)

if st.session_state.get("show_economy_info", False):
    with st.container(border=True):
        st.subheader("Как работи политико-икономическият модел")

        st.markdown("""
        Този симулатор представя Пустиняково като държава, в която политическите решения, регионалните показатели и националният бюджет са свързани. Идеята е, че всяко решение на Конгреса, Президента или правителството трябва да има цена, ефект и политически последици.

        ### 1. Национална икономика

        Националният панел показва общото фискално и политическо състояние на държавата.

        **Свободен фискален ресурс** показва колко пари има правителството за нови политики без да тегли нов дълг. Когато се прилага решение с цена, тази стойност намалява.

        **БВП** показва мащаба на икономиката. Той е важен, защото държавният дълг сам по себе си не е достатъчен показател — важна е връзката между дълга и размера на икономиката.

        **Годишни приходи** са средствата, които държавата очаква да събере чрез данъци, такси, държавни дружества и други източници.

        **Годишни разходи** са вече поетите разходи на държавата — администрация, социална политика, инфраструктура, субсидии, сигурност и други постоянни пера.

        **Дефицит** се изчислява като разлика между годишните разходи и годишните приходи. Ако разходите са по-високи от приходите, държавата има дефицит.

        **Държавен дълг** показва натрупаните задължения на държавата. Ако политиките се финансират чрез заем, дългът трябва да расте.

        **Дълг към БВП** показва колко тежък е дългът спрямо икономиката. Това е по-важен показател от самия размер на дълга.

        **Инфлация** показва ценовия натиск в икономиката. Тя може да се повишава при дългово финансиране, кризи, недостиг на стоки, енергийни шокове или прекалено големи публични разходи.

        **Данъчна тежест** показва колко силно гражданите и фирмите усещат данъчната система. По-високата данъчна тежест може да увеличи приходите, но може да намали икономическата активност и да повиши напрежението.

        **Аварийен резерв** е отделен ресурс за извънредни ситуации — природни бедствия, енергийни кризи, срив на обществени услуги или регионални извънредни мерки.

        **Политически капитал** измерва способността на управляващите да прокарват трудни решения. Той намалява при непопулярни реформи, регионално пренасочване на средства, данъчни увеличения, скандали и конфликти.

        **Национална стабилност** показва общата устойчивост на държавата. Тя пада, когато има високо напрежение, бюджетни проблеми, регионални кризи или политическа парализа.

        **Легитимност** показва доколко управлението изглежда приемливо и оправдано за обществото.

        ### 2. Регионална икономика

        Всяка област има собствени показатели. Те показват не само икономическото състояние, но и политическата среда.

        **Икономика** измерва общото развитие на областта. Ниска стойност означава слаб растеж, бедност, ниска заетост и риск от недоволство.

        **Инфраструктура** показва качеството на пътища, транспорт, публични сгради, комуникации и базови условия за развитие.

        **Обществени услуги** показват здравеопазване, образование, администрация, социална подкрепа и местен капацитет. Ако тази стойност падне прекалено ниско, може да се появи активна криза.

        **Индустриално производство** показва фабрики, мини, енергетика, логистика и стратегически производствени мощности.

        **Безработица** е рисков показател — колкото е по-висока, толкова по-голям е рискът от бедност, миграция, протестен вот и социално напрежение.

        **Обществено напрежение** измерва непосредствената нестабилност. Високо напрежение в комбинация със силна опозиция може да доведе до масови протести.

        **Корупция** показва злоупотреби, непрозрачни обществени поръчки, местни зависимости и неефективност на публичните средства.

        ### 3. Политически показатели

        **Доверие в режима** показва подкрепата за централната власт. Ниско доверие прави протестите, опозиционната мобилизация и регионалното неподчинение по-вероятни.

        **Сила на опозицията** показва дали в областта има организирани актьори, които могат да превърнат недоволството в политическо действие.

        **Патронаж** показва зависимости, контролирани мрежи, клиентелизъм, местни елити и зависимост от властта. Високият патронаж може временно да стабилизира властта, но усилва корупцията и институционалното овладяване.

        **Политическа волатилност** показва колко лесно избирателите могат да сменят политическата си подкрепа.

        **Местна идентичност** показва силата на регионалната принадлежност. Ако е висока, а доверието в централната власт е ниско, областта може да стане по-склонна към регионално противопоставяне.

        ### 4. Как решенията променят системата

        Когато се приложи решение, симулаторът променя избран регионален показател и намалява свободния фискален ресурс с посочената цена. Промените се записват в `regions.json`, `country.json` и `decisions_log.json`, така че остават активни и след рестарт на приложението.

        В бъдещата логика едно решение няма да променя само един показател. Например инфраструктурна инвестиция може да увеличи инфраструктурата, да подобри икономиката, да намали безработицата, но и да увеличи корупционния риск. Регионално пренасочване на средства може да помогне на една област, но да влоши услугите, доверието и напрежението в друга.

        ### 5. Активни събития

        Активните събития не са произволни. Те се появяват, когато дадена област премине определени прагове.

        Например:

        - ниска икономика + висока безработица → регионална икономическа криза
        - високо обществено напрежение + силна опозиция → масови протести
        - много ниски обществени услуги → криза в обществените услуги
        - висока корупция + ниско доверие → корупционен скандал
        - висок патронаж + висока корупция + високо доверие в режима → патронажно овладяна област

        Така картата не е просто визуализация, а система за политически последствия: решенията променят показатели, показателите създават събития, а събитията могат по-късно да влияят върху избори, стабилност и нови политически решения.
        """)

st.divider()

map_image = Image.open("assets/map.png")

original_width, original_height = map_image.size

display_width = DISPLAY_WIDTH
display_height = int(original_height * display_width / original_width)

scale_x = original_width / display_width
scale_y = original_height / display_height

st.sidebar.title("Информация за областта")
st.sidebar.write("Кликни върху област, за да видиш нейния политически и икономически профил.")

clicked = streamlit_image_coordinates(
    map_image,
    width=display_width,
    key="strategy_map"
)

if clicked is not None:
    displayed_x = clicked["x"]
    displayed_y = clicked["y"]

    # Convert displayed coordinates back to original image coordinates
    original_x = int(displayed_x * scale_x)
    original_y = int(displayed_y * scale_y)

    st.write(f"Клик върху показаната карта: x={displayed_x}, y={displayed_y}")
    st.write(f"Клик върху оригиналната карта: x={original_x}, y={original_y}")

    selected_region = find_region_by_click(original_x, original_y, regions)

    if selected_region:
        st.sidebar.subheader(selected_region["name"])

        st.sidebar.write(f"**Партия на губернатора:** {selected_region.get('governor_party', 'Неизвестно')}")
        st.sidebar.write(f"**Население:** {selected_region.get('population', 0):,}")

        st.sidebar.divider()
        st.sidebar.subheader("Икономика и общество")
        st.sidebar.markdown(format_indicator("Икономика", selected_region.get("economy", 0)))
        st.sidebar.markdown(format_indicator("Образование", selected_region.get("education", 0)))
        st.sidebar.markdown(format_indicator("Урбанизация", selected_region.get("urbanization", 0)))
        st.sidebar.markdown(format_indicator("Фискален капацитет", selected_region.get("fiscal_capacity", 0)))
        st.sidebar.markdown(format_indicator("Зависимост от централната държава", selected_region.get("state_dependency", 0), higher_is_bad=True))
        st.sidebar.markdown(format_indicator("Инфраструктура", selected_region.get("infrastructure", 0)))
        st.sidebar.markdown(format_indicator("Обществени услуги", selected_region.get("public_services", 0)))
        st.sidebar.markdown(format_indicator("Индустриално производство", selected_region.get("industrial_output", 0)))
        st.sidebar.markdown(
            format_indicator("Безработица", selected_region.get("unemployment", 0), suffix="%", higher_is_bad=True))
        st.sidebar.markdown(
            format_indicator("Обществено напрежение", selected_region.get("unrest", 0), higher_is_bad=True))
        st.sidebar.markdown(format_indicator("Корупция", selected_region.get("corruption", 0), higher_is_bad=True))

        st.sidebar.divider()
        st.sidebar.subheader("Политически профил")
        st.sidebar.markdown(format_indicator("Избирателна активност", selected_region.get("turnout", 0), suffix="%"))
        st.sidebar.markdown(format_indicator("Политическа волатилност", selected_region.get("political_volatility", 0),
                                             higher_is_bad=True))
        st.sidebar.markdown(
            format_indicator("Традиционализъм", selected_region.get("traditionalism", 0), higher_is_bad=False))
        st.sidebar.markdown(
            format_indicator("Прогресивизъм", selected_region.get("progressivism", 0), higher_is_bad=False))
        st.sidebar.markdown(format_indicator("Доверие в режима", selected_region.get("regime_trust", 0)))
        st.sidebar.markdown(
            format_indicator("Сила на опозицията", selected_region.get("opposition_strength", 0), higher_is_bad=True))
        st.sidebar.markdown(format_indicator("Патронаж", selected_region.get("patronage", 0), higher_is_bad=True))
        st.sidebar.markdown(
            format_indicator("Местна идентичност", selected_region.get("local_identity", 0), higher_is_bad=True))
        st.sidebar.markdown(
            format_indicator("Мюсюлманско население", selected_region.get("muslim_share", 0), suffix="%",
                             higher_is_bad=False))

        st.sidebar.divider()
        st.sidebar.subheader("Активни събития")

        active_events = get_active_events(selected_region)

        if active_events:
            for event in active_events:
                st.sidebar.markdown(f"**{event['level']} {event['title']}**")
                st.sidebar.caption(event["reason"])
        else:
            st.sidebar.success("Няма активни събития.")
    else:
        st.sidebar.warning("На това място не е открита област.")
else:
    st.info("Кликни някъде върху картата.")

st.divider()
st.subheader("Прилагане на решение")

with st.form("apply_decision_form"):
    decision_title = st.text_input("Име на решението / закона")
    target_region_name = st.selectbox(
        "Целева област",
        [region["name"] for region in regions]
    )
    indicator_label = st.selectbox(
        "Показател за промяна",
        list(INDICATOR_LABELS.values())
    )

    indicator = next(
        key for key, value in INDICATOR_LABELS.items()
        if value == indicator_label
    )

    change_value = st.number_input("Промяна на показателя", value=0, step=1)
    cost = st.number_input("Цена на решението в млн.", min_value=0, value=0, step=50)

    funding_source_label = st.selectbox(
        "Източник на финансиране",
        [
            "Бюджет",
            "Дълг",
            "Аварийен резерв",
            "Символично/регулаторно решение"
        ]
    )

    submitted = st.form_submit_button("Приложи решение")

    if submitted:
        target_region = None

        for region in regions:
            if region["name"] == target_region_name:
                target_region = region
                break

        if target_region is not None:
            old_value = target_region.get(indicator, 0)
            new_value = old_value + change_value

            if indicator != "unemployment":
                new_value = max(0, min(100, new_value))
            else:
                new_value = max(0, new_value)

            if funding_source_label == "Бюджет" and cost > country.get("treasury_balance", 0):
                st.error(
                    "Недостатъчен свободен фискален ресурс. "
                    "Избери друг източник на финансиране или намали цената на решението."
                )
                st.stop()

            if funding_source_label == "Аварийен резерв" and cost > country.get("emergency_reserve", 0):
                st.error(
                    "Недостатъчен аварийен резерв. "
                    "Избери друг източник на финансиране или намали цената на решението."
                )
                st.stop()

            target_region[indicator] = new_value

            fiscal_effect_note = ""

            if funding_source_label == "Бюджет":
                country["treasury_balance"] = country.get("treasury_balance", 0) - cost
                fiscal_effect_note = f"Свободен фискален ресурс: -{cost} млн."

            elif funding_source_label == "Дълг":
                country["public_debt"] = country.get("public_debt", 0) + cost
                country["annual_spending"] = country.get("annual_spending", 0) + cost
                country["inflation"] = round(country.get("inflation", 0) + (cost / 1000), 1)
                fiscal_effect_note = f"Държавен дълг: +{cost} млн."

            elif funding_source_label == "Аварийен резерв":
                country["emergency_reserve"] = country.get("emergency_reserve", 0) - cost
                fiscal_effect_note = f"Аварийен резерв: -{cost} млн."

            elif funding_source_label == "Символично/регулаторно решение":
                fiscal_effect_note = "Няма пряк фискален разход."

            country = update_derived_country_values(country)

            decision_record = {
                "title": decision_title,
                "target_region": target_region_name,
                "indicator": indicator,
                "indicator_label": indicator_label,
                "old_value": old_value,
                "change_value": change_value,
                "new_value": new_value,
                "cost_millions": cost,
                "funding_source": funding_source_label,
                "fiscal_effect_note": fiscal_effect_note
            }

            decisions_log.append(decision_record)

            save_regions(regions)
            save_country(country)
            save_decisions_log(decisions_log)

            st.success(
                f"Решението '{decision_title}' беше приложено: "
                f"{target_region_name} → {indicator_label}: {old_value} → {new_value}. "
                f"{fiscal_effect_note}"
            )
            st.rerun()


st.divider()
st.subheader("Прилагане на политически шаблон")

# These selectors stay outside the form so Streamlit can rerun immediately
# and update the explanation and show/hide the relevant region selection fields.
template_scope = st.selectbox(
    "Обхват на прилагане",
    [
        "Една област",
        "Избрани области",
        "Всички области",
        "Области с висока безработица",
        "Области с висока корупция",
        "Индустриални области",
        "Силно зависими от централната държава области"
    ],
    key="template_scope_select"
)

template_label = st.selectbox(
    "Тип политически шаблон",
    [template["label"] for template in POLICY_TEMPLATES.values()],
    key="template_label_select"
)

template_key = next(
    key for key, value in POLICY_TEMPLATES.items()
    if value["label"] == template_label
)

selected_template = POLICY_TEMPLATES[template_key]

with st.container(border=True):
    st.markdown(f"**Детайли:** {selected_template['description']}")

with st.form("policy_template_form"):
    template_law_id = st.text_input("Закон / Решение на Върховния Конгрес (ID)", key="template_law_id_input")

    template_single_region_name = None
    template_selected_region_names = []

    if template_scope == "Една област":
        template_single_region_name = st.selectbox(
            "Целева област",
            [region["name"] for region in regions],
            key="template_single_region_select"
        )

    elif template_scope == "Избрани области":
        template_selected_region_names = st.multiselect(
            "Избери области",
            [region["name"] for region in regions],
            key="template_multi_region_select"
        )

    elif template_scope == "Всички области":
        st.info("Шаблонът ще бъде приложен към всички области.")

    elif template_scope == "Области с висока безработица":
        matching_regions = [region["name"] for region in regions if region.get("unemployment", 0) > 20]
        st.info(f"Шаблонът ще бъде приложен към: {', '.join(matching_regions) if matching_regions else 'няма области'}")

    elif template_scope == "Области с висока корупция":
        matching_regions = [region["name"] for region in regions if region.get("corruption", 0) > 60]
        st.info(f"Шаблонът ще бъде приложен към: {', '.join(matching_regions) if matching_regions else 'няма области'}")

    elif template_scope == "Индустриални области":
        matching_regions = [region["name"] for region in regions if region.get("industrial_output", 0) > 55]
        st.info(f"Шаблонът ще бъде приложен към: {', '.join(matching_regions) if matching_regions else 'няма области'}")

    elif template_scope == "Силно зависими от централната държава области":
        matching_regions = [region["name"] for region in regions if region.get("state_dependency", 0) > 65]
        st.info(f"Шаблонът ще бъде приложен към: {', '.join(matching_regions) if matching_regions else 'няма области'}")

    template_cost = st.number_input(
        "Цена на политиката в млн.",
        min_value=0,
        value=0,
        step=50,
        key="template_cost_input"
    )

    template_funding_source = st.selectbox(
        "Източник на финансиране за шаблона",
        [
            "Бюджет",
            "Дълг",
            "Аварийен резерв",
            "Символично/регулаторно решение"
        ],
        key="template_funding_select"
    )

    template_submitted = st.form_submit_button("Приложи политически шаблон")

    if template_submitted:
        target_regions = []

        if template_scope == "Една област":
            target_regions = [
                region for region in regions
                if region["name"] == template_single_region_name
            ]

        elif template_scope == "Избрани области":
            target_regions = [
                region for region in regions
                if region["name"] in template_selected_region_names
            ]

        elif template_scope == "Всички области":
            target_regions = regions

        elif template_scope == "Области с висока безработица":
            target_regions = [
                region for region in regions
                if region.get("unemployment", 0) > 20
            ]

        elif template_scope == "Области с висока корупция":
            target_regions = [
                region for region in regions
                if region.get("corruption", 0) > 60
            ]

        elif template_scope == "Индустриални области":
            target_regions = [
                region for region in regions
                if region.get("industrial_output", 0) > 55
            ]

        elif template_scope == "Силно зависими от централната държава области":
            target_regions = [
                region for region in regions
                if region.get("state_dependency", 0) > 65
            ]

        if not target_regions:
            st.error("Няма области, които отговарят на избрания обхват.")
            st.stop()

        if template_funding_source == "Бюджет" and template_cost > country.get("treasury_balance", 0):
            st.error(
                "Недостатъчен свободен фискален ресурс. "
                "Избери друг източник на финансиране или намали цената на политиката."
            )
            st.stop()

        if template_funding_source == "Аварийен резерв" and template_cost > country.get("emergency_reserve", 0):
            st.error(
                "Недостатъчен аварийен резерв. "
                "Избери друг източник на финансиране или намали цената на политиката."
            )
            st.stop()

        applied_effects = {}

        for target_region in target_regions:
            region_name = target_region["name"]
            applied_effects[region_name] = {}

            for indicator, effect in selected_template["regional_effects"].items():
                old_value = target_region.get(indicator, 0)
                new_value = clamp(old_value + effect)
                target_region[indicator] = new_value

                applied_effects[region_name][indicator] = {
                    "old_value": old_value,
                    "change": effect,
                    "new_value": new_value
                }

        for country_indicator, effect in selected_template["country_effects"].items():
            old_value = country.get(country_indicator, 0)
            country[country_indicator] = clamp(old_value + effect)

        fiscal_effect_note = ""

        if template_funding_source == "Бюджет":
            country["treasury_balance"] = country.get("treasury_balance", 0) - template_cost
            fiscal_effect_note = f"Свободен фискален ресурс: -{template_cost} млн."

        elif template_funding_source == "Дълг":
            country["public_debt"] = country.get("public_debt", 0) + template_cost
            country["annual_spending"] = country.get("annual_spending", 0) + template_cost
            country["inflation"] = round(country.get("inflation", 0) + (template_cost / 1000), 1)
            fiscal_effect_note = f"Държавен дълг: +{template_cost} млн."

        elif template_funding_source == "Аварийен резерв":
            country["emergency_reserve"] = country.get("emergency_reserve", 0) - template_cost
            fiscal_effect_note = f"Аварийен резерв: -{template_cost} млн."

        elif template_funding_source == "Символично/регулаторно решение":
            fiscal_effect_note = "Няма пряк фискален разход."

        country = update_derived_country_values(country)

        template_record = {
            "title": template_label,
            "law_id": template_law_id,
            "type": "policy_template",
            "template_key": template_key,
            "scope": template_scope,
            "target_regions": [region["name"] for region in target_regions],
            "cost_millions": template_cost,
            "funding_source": template_funding_source,
            "fiscal_effect_note": fiscal_effect_note,
            "applied_effects": applied_effects
        }

        decisions_log.append(template_record)

        save_regions(regions)
        save_country(country)
        save_decisions_log(decisions_log)

        st.success(
            f"Политическият шаблон '{template_label}' беше приложен към {len(target_regions)} област(и). "
            f"{fiscal_effect_note}"
        )
        st.rerun()

st.divider()
st.subheader("Фискални действия")

with st.form("fiscal_action_form"):
    fiscal_action_label = st.selectbox(
        "Тип фискално действие",
        list(FISCAL_ACTIONS.values())
    )

    fiscal_law_id = st.text_input("Закон / Решение на Върховния Конгрес (ID)", key="fiscal_law_id_input")

    fiscal_action_key = next(
        key for key, value in FISCAL_ACTIONS.items()
        if value == fiscal_action_label
    )

    fiscal_amount = st.number_input(
        "Сума в млн.",
        min_value=0,
        value=0,
        step=50
    )

    fiscal_submitted = st.form_submit_button("Приложи фискално действие")
    if fiscal_submitted:
        fiscal_note = ""

        if fiscal_action_key == "tax_increase":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["annual_revenue"] = country.get("annual_revenue", 0) + round(fiscal_amount * 0.5)
            country["tax_burden"] = clamp(country.get("tax_burden", 0) + 2)
            country["government_legitimacy"] = clamp(country.get("government_legitimacy", 0) - 1)
            country["national_stability"] = clamp(country.get("national_stability", 0) - 1)
            fiscal_note = f"Данъците бяха увеличени. Свободният фискален ресурс се повиши с {fiscal_amount} млн."

        elif fiscal_action_key == "spending_cuts":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["annual_spending"] = max(0, country.get("annual_spending", 0) - fiscal_amount)
            country["government_legitimacy"] = clamp(country.get("government_legitimacy", 0) - 2)
            country["national_stability"] = clamp(country.get("national_stability", 0) - 2)

            for region in regions:
                region["public_services"] = clamp(region.get("public_services", 0) - 2)
                region["unrest"] = clamp(region.get("unrest", 0) + 2)

            fiscal_note = f"Публичните разходи бяха съкратени. Свободният фискален ресурс се повиши с {fiscal_amount} млн., но обществените услуги се влошиха."

        elif fiscal_action_key == "debt_issue":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["public_debt"] = country.get("public_debt", 0) + fiscal_amount
            country["annual_spending"] = country.get("annual_spending", 0) + round(fiscal_amount * 0.05)
            country["inflation"] = round(country.get("inflation", 0) + (fiscal_amount / 1000), 1)
            fiscal_note = f"Държавата емитира нов дълг за {fiscal_amount} млн."

        elif fiscal_action_key == "emergency_transfer":
            if fiscal_amount > country.get("emergency_reserve", 0):
                st.error(
                    "Недостатъчен аварийен резерв. "
                    "Не можеш да прехвърлиш повече средства, отколкото има в резерва."
                )
                st.stop()

            transfer_amount = fiscal_amount
            country["treasury_balance"] = country.get("treasury_balance", 0) + transfer_amount
            country["emergency_reserve"] = country.get("emergency_reserve", 0) - transfer_amount

            if country.get("emergency_reserve", 0) < 150:
                country["national_stability"] = clamp(country.get("national_stability", 0) - 2)

            fiscal_note = f"От аварийния резерв бяха прехвърлени {transfer_amount} млн. към свободния фискален ресурс."

        elif fiscal_action_key == "anti_corruption_recovery":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["political_capital"] = clamp(country.get("political_capital", 0) - 5)
            country["government_legitimacy"] = clamp(country.get("government_legitimacy", 0) + 2)

            for region in regions:
                region["corruption"] = clamp(region.get("corruption", 0) - 3)
                region["patronage"] = clamp(region.get("patronage", 0) - 2)

                if region.get("patronage", 0) > 65:
                    region["unrest"] = clamp(region.get("unrest", 0) + 2)

            fiscal_note = f"Антикорупционните мерки възстановиха {fiscal_amount} млн., но струваха политически капитал."

        elif fiscal_action_key == "privatization":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["annual_revenue"] = max(0, country.get("annual_revenue", 0) - round(fiscal_amount * 0.05))
            country["government_legitimacy"] = clamp(country.get("government_legitimacy", 0) - 2)

            for region in regions:
                region["corruption"] = clamp(region.get("corruption", 0) + 1)
                region["unrest"] = clamp(region.get("unrest", 0) + 1)

            fiscal_note = f"Приватизацията донесе {fiscal_amount} млн., но създаде риск от корупция и обществено недоволство."

        elif fiscal_action_key == "state_enterprise_dividend":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["annual_revenue"] = country.get("annual_revenue", 0) + round(fiscal_amount * 0.15)

            for region in regions:
                if region.get("industrial_output", 0) > 55:
                    region["industrial_output"] = clamp(region.get("industrial_output", 0) - 1)
                    region["infrastructure"] = clamp(region.get("infrastructure", 0) - 1)

            fiscal_note = f"Държавните предприятия внесоха извънреден дивидент от {fiscal_amount} млн."

        elif fiscal_action_key == "regional_levy":
            country["treasury_balance"] = country.get("treasury_balance", 0) + fiscal_amount
            country["political_capital"] = clamp(country.get("political_capital", 0) - 3)

            for region in regions:
                if region.get("economy", 0) > 55 or region.get("industrial_output", 0) > 55:
                    region["economy"] = clamp(region.get("economy", 0) - 1)
                    region["regime_trust"] = clamp(region.get("regime_trust", 0) - 3)
                    region["unrest"] = clamp(region.get("unrest", 0) + 3)
                    region["local_identity"] = clamp(region.get("local_identity", 0) + 2)
                    region["opposition_strength"] = clamp(region.get("opposition_strength", 0) + 2)

            fiscal_note = f"Централният бюджет събра извънредна регионална вноска от {fiscal_amount} млн."

        country = update_derived_country_values(country)

        fiscal_record = {
            "title": fiscal_action_label,
            "law_id": fiscal_law_id,
            "type": "fiscal_action",
            "action_key": fiscal_action_key,
            "amount_millions": fiscal_amount,
            "note": fiscal_note
        }

        decisions_log.append(fiscal_record)

        save_regions(regions)
        save_country(country)
        save_decisions_log(decisions_log)

        st.success(fiscal_note)
        st.rerun()