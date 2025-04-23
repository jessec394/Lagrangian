'''  Script to solve the equations of motion for an any-DOF system of generalized coordinates  '''
'''  Jesse Cook (2025) '''

# Usage Instructions
'''
1.) Define symbolic constants in the "Constants" list
    eg. 'g' or 'L' representing static quantities with no time derivative

2.) Define symbolic variables in the "Variables" list
    eg. 'x' or 'theta' representing functions of time

3.) Define energy expressions in the "KineticEnergy" and "PotentialEnergy" lists
    Resolve all expressions in an inertial reference frame
    Use "_dot" and "_ddot" to represent first and second time derivatives of defined variables
'''

# Libraries
import matplotlib.pyplot as plt
from matplotlib.offsetbox import AnchoredText
import os
import sympy as sp

# Project Directory
Directory = os.path.abspath(os.path.dirname(__file__))
SavePath = os.path.join(Directory, "Output.png")

''' --------------- '''
''' BEGIN USER INPUT'''
''' --------------- '''

# Constant Terms
Constants = [
    'g',
    'L_1',
    'L_2',
    'm_1',
    'm_2'
]

# Variable Terms
Variables = [
    'theta',
    'phi'
]

# Kinetic Energy Expressions
KineticEnergy = [
    '(0.5 * m_1 * L_1^2 * theta_dot**2)',
    '(0.5 * m_2 * L_1^2 * theta_dot**2)',
    '(0.5 * m_2 * L_2^2 * phi_dot**2)',
    '(m_2 * L_1 * L_2 * theta_dot * phi_dot * cos(theta - phi))'
]

# Potential Energy Expressions
PotentialEnergy = [
    '(-m_1 * g * L_1 * cos(theta))',
    '(-m_2 * g * L_1 * cos(theta))',
    '(-m_2 * g * L_2 * cos(phi))'
]

''' ------------- '''
''' END USER INPUT'''
''' ------------- '''

# Time
t = sp.symbols('t')

# Generalized Coordinates
q = sp.symbols(f'q1:{len(Variables)+1}', cls=sp.Function)
q_dot = [sp.diff(q_i(t), t) for q_i in q]
q_ddot = [sp.diff(qd, t) for qd in q_dot]

# Sympy-ify Terms
SympyDict = {
    **{f"{Variables[i]}": q[i](t) for i in range(len(q))},
    **{f"{Variables[i]}_dot": q_dot[i] for i in range(len(q))},
    **{f"{Variables[i]}_ddot": q_ddot[i] for i in range(len(q))},

    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "sec": sp.sec,
    "csc": sp.csc,
    "cot": sp.cot,

    "^": '**'
}

# LaTeX-ify Terms
def SpecialCharacters(Symbol):
    Characters = [
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu', 'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma', 'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega',
        'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega'
    ]
    for c in Characters:
        if c in Symbol: Symbol = f'\\{Symbol}'; break
    return Symbol

# Constants and Variables
Constants = [SpecialCharacters(c) for c in Constants]
Variables = [SpecialCharacters(v) for v in Variables]

# Kinetic and Potential Energy
T = sum([sp.sympify(term, locals=SympyDict) for term in KineticEnergy])
V = sum([sp.sympify(term, locals=SympyDict) for term in PotentialEnergy])

# Lagrangian
L = T - V

# Equations of Motion
EOM = []

# Remove LaTeX Junk
def Format(Expression):
    LatexString = sp.latex(sp.simplify(Expression))                         # Simplify Expression                           [2x/4 -> x/2]
    LatexString = LatexString.replace(r'{\left(t \right)}', '')             # Eliminate Function Notation                   [x(t) -> x]
    LatexString = LatexString.replace(r'1.0', '')                           # Remove 1.0 Coefficient                        [1.0x -> x]
    LatexString = LatexString.replace(r'\cdot', '')                         # Remove Multiplication Dot                     [x·y -> xy]
    LatexString = LatexString.replace(r'\frac{d}{d t}', r'\dot')            # Replace 1st Time Derivative with Single Dot   [dx/dt -> x_dot]
    LatexString = LatexString.replace(r'\frac{d^{2}}{d t^{2}}', r'\ddot')   # Replace 2nd Time Derivative with Double Dot   [d^2x/dt^2 -> x_ddot]

    # Replace Generalized Coordinates with Variable Names
    for i in range(len(Variables)):
        VariableString = str(Variables[i])
        LatexString = LatexString.replace(f'q_{{{i+1}}}', VariableString)
        LatexString = LatexString.replace(f'\\dot{{q}}_{{{i+1}}}', f'\\dot{{{VariableString}}}')
        LatexString = LatexString.replace(f'\\ddot{{q}}_{{{i+1}}}', f'\\ddot{{{VariableString}}}')

    return LatexString

# Initialize Plot
fig, ax = plt.subplots(figsize=(12, 8))

fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.grid(visible=False)

ax.axis("off")

Title = f'Equation of Motion Solver ({len(Variables)} DOF)\n'

def Divider(Length=len(Title)):
    Line = f'\n'
    for i in range(Length): Line += '--'
    Line += '\n'
    return Line

# Beginning Text
Text = Title

Text += Divider()

Text += f'\nGeneralized Coordinates: ' + r'$\left('
for i in range(len(Variables)):
    Text += f'{Variables[i]}'
    if i < len(Variables)-1: Text += f', '
Text += r'\right)$' + f'\n'

Text += f'\nConstants: ' + r'$\left('
for i in range(len(Constants)):
    Text += f'{Constants[i]}'
    if i < len(Constants)-1: Text += f', '
Text += r'\right)$' + f'\n'

Text += f"\nKinetic and Potential Energy:\n"
Text += f'\t' + r'$\mathcal{T} = $' + f'${Format(T)}$\n'
Text += f'\t' + r'$\mathcal{V} = $' + f'${Format(V)}$\n'

Text += f'\nLagrangian:\n'
Text += f'\t' + r'$\mathcal{{L}} = \mathcal{{T}} - \mathcal{{V}} = $' + f'${Format(L)}$\n'

Text += Divider()

# For Each Generalized Coordinate:
for i in range(len(Variables)):
    # GC as a Function of Time
    qi = q[i](t)

    # First Time Derivative
    qi_dot = q_dot[i]

    # Second Time Derivative
    qi_ddot = q_ddot[i]

    # (1) Partial L / Partial q_dot
    dL_dqi_dot = (sp.diff(L, qi_dot))

    # (2) Partial L / Partial q
    dL_dqi = (sp.diff(L, qi))

    # (3) Time Derivative of (1)
    d_dt_dL_dqi_dot = (sp.diff(dL_dqi_dot, t))

    # (3) - (2) = 0
    EOM.append(sp.Eq(0, (d_dt_dL_dqi_dot - dL_dqi)))

    # Case-Specific Text
    Text += f'\nFor $q_{i+1} = {Variables[i]}$:\n'
    Text += f'\t$\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{{q}}}}_{{{i+1}}}}} = {Format(dL_dqi_dot)}$\n'
    Text += f'\t$\\frac{{\\partial \\mathcal{{L}}}}{{\\partial q_{{{i+1}}}}} = {Format(dL_dqi)}$\n'
    Text += f'\t$\\frac{{d}}{{dt}}\\left(\\frac{{\\partial \\mathcal{{L}}}}{{\\partial \\dot{{{{q}}}}_{{{i+1}}}}}\\right) = {Format(d_dt_dL_dqi_dot)}$\n'

Text += Divider()

# Display EOMs
Text += f'\nEquations of Motion: '
Text += r'$\frac{d}{dt}\left(\frac{\partial \mathcal{L}}{\partial \dot{q}_i}\right) - \frac{\partial \mathcal{L}}{\partial q_{i}} = 0$' + f'\n'

for i in range(len(Variables)):
    Text += f'\n\t' + r'$\left(' + f'{Variables[i]}' + r'\right)$: '
    Text += f'${Format(sp.simplify(EOM[i]))}$\n'

# Text Box
Textbox = AnchoredText(Text, loc="center", prop=dict(size=14, family="serif"), frameon=True, pad=0.5, bbox_to_anchor=(0.5, 0.5), bbox_transform=ax.transAxes)
Textbox.patch.set_boxstyle("round,pad=0.5")
Textbox.patch.set_facecolor("#ffffff")
Textbox.patch.set_edgecolor("#000000")
Textbox.patch.set_alpha(1.0)

ax.add_artist(Textbox)

# Save Figure
plt.savefig(SavePath, bbox_inches="tight", dpi=300, transparent=True)

# Open Figure
if os.name == "posix": os.system(f'xdg-open "{SavePath}"')
elif os.name == "nt": os.system(f'start "" "{SavePath}"')
