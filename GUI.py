import os
import sympy as sp
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import pygame
import pygame_gui

# Project Directory
Directory = os.path.abspath(os.path.dirname(__file__))
SavePath = os.path.join(Directory, "Magic.png")

# Initialize GUI
pygame.font.init()
pygame.mixer.init()
pygame.joystick.init()
pygame.init()

Width = pygame.display.Info().current_w
Height = Width * (9 / 16)
SF = min(Width / 1920, Height / 1080)
Window = pygame.display.set_mode((Width, Height))

pygame.display.set_caption("EOM Solver GUI")
pygame.mouse.set_pos((Width, Height))

Manager = pygame_gui.UIManager((Width, Height))

Clock = pygame.time.Clock()
Running = False

# Startup Function
def Startup():
    global Running
    Running = True

# Shutdown Function
def Shutdown():
    global Running
    Running = False

# UI Elements
ColorBackground = '#36454F'
ColorOutputFace = '#FFFFFF'
ColorOutputEdge = '#000000'

# Input Fields and Buttons
UserInputs = [
    {"type": "input", "name": "Constant", "pos": (50, 50), "size": (200, 30)},
    {"type": "input", "name": "Variable", "pos": (50, 100), "size": (200, 30)},
    {"type": "input", "name": "Kinetic", "pos": (50, 150), "size": (200, 30)},
    {"type": "input", "name": "Potential", "pos": (50, 200), "size": (200, 30)},

    {"type": "button", "name": "AddConstant", "pos": (270, 50), "size": (100, 30), "text": "+ Constant"},
    {"type": "button", "name": "AddVariable", "pos": (270, 100), "size": (100, 30), "text": "+ Variable"},
    {"type": "button", "name": "AddKinetic", "pos": (270, 150), "size": (100, 30), "text": "+ Kinetic"},
    {"type": "button", "name": "AddPotential", "pos": (270, 200), "size": (100, 30), "text": "+ Potential"},

    {"type": "list", "name": "Constant", "pos": (520, 50), "size": (200, 100)},
    {"type": "list", "name": "Variable", "pos": (520, 160), "size": (200, 100)},
    {"type": "list", "name": "Kinetic", "pos": (520, 270), "size": (200, 100)},
    {"type": "list", "name": "Potential", "pos": (520, 380), "size": (200, 100)},

    {"type": "button", "name": "RemoveConstant", "pos": (740, 50), "size": (100, 30), "text": "- Constant"},
    {"type": "button", "name": "RemoveVariable", "pos": (740, 160), "size": (100, 30), "text": "- Variable"},
    {"type": "button", "name": "RemoveKinetic", "pos": (740, 270), "size": (100, 30), "text": "- Kinetic"},
    {"type": "button", "name": "RemovePotential", "pos": (740, 380), "size": (100, 30), "text": "- Potential"},

    {"type": "button", "name": "Generate", "pos": (50, 250), "size": (200, 40), "text": "Generate EOM"}
]

# Initialize UI Elements
InputFields = {}
Buttons = {}
SelectionLists = {}

for element in UserInputs:
    if element["type"] == "input":
        InputFields[element["name"]] = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((element["pos"][0] * SF, element["pos"][1] * SF), (element["size"][0] * SF, element["size"][1] * SF)), manager=Manager)
    elif element["type"] == "button":
        Buttons[element["name"]] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((element["pos"][0] * SF, element["pos"][1] * SF), (element["size"][0] * SF, element["size"][1] * SF)), text=element["text"], manager=Manager)
    elif element["type"] == "list":
        SelectionLists[element["name"]] = pygame_gui.elements.UISelectionList(relative_rect=pygame.Rect((element["pos"][0] * SF, element["pos"][1] * SF), (element["size"][0] * SF, element["size"][1] * SF)), item_list=[], manager=Manager)

Constants, Variables, KineticEnergy, PotentialEnergy = [], [], [], []

def SpecialCharacters(Symbol):
    Characters = [
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
    ]
    for c in Characters:
        if c in Symbol: Symbol = f'\\{Symbol}'; break
    return Symbol

def FormatExpression(Expression, Variables):
    LatexString = sp.latex(sp.simplify(Expression))
    LatexString = LatexString.replace(r'{\left(t \right)}', '')
    LatexString = LatexString.replace(r'1.0', '')
    LatexString = LatexString.replace(r'\cdot', '')
    LatexString = LatexString.replace(r'\frac{d}{d t}', r'\dot')
    LatexString = LatexString.replace(r'\frac{d^{2}}{d t^{2}}', r'\ddot')
    for i, var in enumerate(Variables):
        LatexString = LatexString.replace(f'q_{{{i+1}}}', str(var))
        LatexString = LatexString.replace(f'\\dot{{q}}_{{{i+1}}}', f'\\dot{{{str(var)}}}')
        LatexString = LatexString.replace(f'\\ddot{{q}}_{{{i+1}}}', f'\\ddot{{{str(var)}}}')
    return LatexString

def GenerateImage(Constants, Variables, KineticEnergy, PotentialEnergy):
    t = sp.symbols('t')

    q = sp.symbols(f'q1:{len(Variables)+1}', cls=sp.Function)
    q_dot = [sp.diff(q_i(t), t) for q_i in q]
    q_ddot = [sp.diff(qd, t) for qd in q_dot]

    SympyDict = {
        **{f"{Variables[i]}": q[i](t) for i in range(len(q))},
        **{f"{Variables[i]}_dot": q_dot[i] for i in range(len(q))},
        **{f"{Variables[i]}_ddot": q_ddot[i] for i in range(len(q))},

        "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
        "sec": sp.sec, "csc": sp.csc, "cot": sp.cot,

        "asin": sp.asin, "acos": sp.acos, "tan": sp.atan,
        "asec": sp.asec, "acsc": sp.acsc, "cot": sp.acot,

        "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
        "sech": sp.sech, "csch": sp.csch, "coth": sp.coth,

        "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
        "asech": sp.asech, "acsch": sp.acsch, "acoth": sp.acoth,

        "atan2": sp.atan2,

        "log": sp.log, "ln": sp.log,

        "exp": sp.exp,

        "^": '**'
    }

    Constants = [SpecialCharacters(c) for c in Constants]
    Variables = [SpecialCharacters(v) for v in Variables]

    T = sum([sp.sympify(term, locals=SympyDict) for term in KineticEnergy])
    V = sum([sp.sympify(term, locals=SympyDict) for term in PotentialEnergy])
    L = T - V

    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    ax.grid(visible=False)
    ax.axis("off")

    Title = r'$\mathbf{Equation\ of\ Motion\ Solver\ }$' + f'({len(Variables)} DOF)\n'

    def Divider(length=len(Title)//2):
        return '\n' + '—' * length + '\n'

    Text = Title
    Text += Divider()
    Text += f'\nGeneralized Coordinates: ' + r'$\left('
    Text += ', '.join(Variables) + r'\right)$' + f'\n'
    Text += f'\nConstants: ' + r'$\left('
    Text += ', '.join(Constants) + r'\right)$' + f'\n'
    Text += f"\nKinetic and Potential Energy:" + f'\n'
    Text += f'\t' + r'$\mathcal{T} = $' + f'${FormatExpression(T, Variables)}$\n'
    Text += f'\t' + r'$\mathcal{V} = $' + f'${FormatExpression(V, Variables)}$\n'

    Text += f'\nLagrangian:\n'
    Text += f'\t' + r'$\mathcal{{L}} = \mathcal{{T}} - \mathcal{{V}} = $' + f'${FormatExpression(L, Variables)}$\n'
    Text += Divider()

    EOM = []
    for i in range(len(Variables)):
        qi = q[i](t)
        qi_dot = q_dot[i]
        qi_ddot = q_ddot[i]

        dL_dqi_dot = sp.diff(L, qi_dot)
        dL_dqi = sp.diff(L, qi)
        d_dt_dL_dqi_dot = sp.diff(dL_dqi_dot, t)

        EOM.append(sp.Eq(0, (d_dt_dL_dqi_dot - dL_dqi)))

        Text += f'\nFor $q_{i+1} = {Variables[i]}$:\n'
        Text += f'\t$\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{{q}}}}_{{{i+1}}}}} = {FormatExpression(dL_dqi_dot, Variables)}$\n'
        Text += f'\t$\\frac{{\\partial \\mathcal{{L}}}}{{\\partial q_{{{i+1}}}}} = {FormatExpression(dL_dqi, Variables)}$\n'
        Text += f'\t$\\frac{{d}}{{dt}}\\left(\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{{q}}}}_{{{i+1}}}}}\\right) = {FormatExpression(d_dt_dL_dqi_dot, Variables)}$\n'

    Text += Divider()
    Text += f'\n' + r'$\mathbf{Equations\ of\ Motion:\ }$'
    Text += r'$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_{i}} = 0$' + f'\n'

    for i in range(len(Variables)):
        Text += f'\n\t' + r'$\left(' + f'{Variables[i]}' + r'\right)$: '
        Text += f'${FormatExpression(sp.simplify(EOM[i]), Variables)}$\n'

    Textbox = AnchoredText(Text, loc="center", prop=dict(size=14, family="serif"), frameon=True, pad=0.5, bbox_to_anchor=(0.5, 0.5), bbox_transform=ax.transAxes)
    Textbox.patch.set_boxstyle("round,pad=0.5")
    Textbox.patch.set_facecolor(ColorOutputFace)
    Textbox.patch.set_edgecolor(ColorOutputEdge)
    Textbox.patch.set_alpha(1.0)

    ax.add_artist(Textbox)
    plt.savefig(SavePath, bbox_inches="tight", dpi=300, transparent=True)

    if os.name == "posix":
        os.system(f'xdg-open "{SavePath}"')
    elif os.name == "nt":
        os.system(f'start "" "{SavePath}"')

Startup()

while Running:
    TimeDelta = Clock.tick(60) / 1000.0
    InputMappings = {
        InputFields["Constant"]: (Constants, SelectionLists["Constant"]),
        InputFields["Variable"]: (Variables, SelectionLists["Variable"]),
        InputFields["Kinetic"]: (KineticEnergy, SelectionLists["Kinetic"]),
        InputFields["Potential"]: (PotentialEnergy, SelectionLists["Potential"]),
    }

    ButtonMappings = {
        Buttons["AddConstant"]: (Constants, SelectionLists["Constant"], InputFields["Constant"]),
        Buttons["AddVariable"]: (Variables, SelectionLists["Variable"], InputFields["Variable"]),
        Buttons["AddKinetic"]: (KineticEnergy, SelectionLists["Kinetic"], InputFields["Kinetic"]),
        Buttons["AddPotential"]: (PotentialEnergy, SelectionLists["Potential"], InputFields["Potential"]),
        Buttons["RemoveConstant"]: (Constants, SelectionLists["Constant"]),
        Buttons["RemoveVariable"]: (Variables, SelectionLists["Variable"]),
        Buttons["RemoveKinetic"]: (KineticEnergy, SelectionLists["Kinetic"]),
        Buttons["RemovePotential"]: (PotentialEnergy, SelectionLists["Potential"]),
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Shutdown()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                FocusedElements = Manager.get_focus_set()
                for InputField, (DataList, ListWidget) in InputMappings.items():
                    if InputField in FocusedElements:
                        DataList.append(InputField.text)
                        ListWidget.set_item_list(DataList)
                        InputField.set_text('')

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in ButtonMappings:
                Mapping = ButtonMappings[event.ui_element]

                # Handle "Add" Buttons
                if len(Mapping) == 3:
                    DataList, ListWidget, InputField = Mapping
                    if InputField.text:
                        DataList.append(InputField.text)
                        ListWidget.set_item_list(DataList)
                        InputField.set_text('')

                # Handle "Remove" Buttons
                elif len(Mapping) == 2:
                    DataList, ListWidget = Mapping
                    Selected = ListWidget.get_single_selection()
                    if Selected:
                        DataList.remove(Selected)
                        ListWidget.set_item_list(DataList)

            elif event.ui_element == Buttons["Generate"]:
                GenerateImage(Constants, Variables, KineticEnergy, PotentialEnergy)

        Manager.process_events(event)

    Manager.update(TimeDelta)
    Window.fill(ColorBackground)
    Manager.draw_ui(Window)
    pygame.display.update()