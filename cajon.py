import os
import requests


def download_icons(icon_names, download_dir='icons'):
    base_url = 'https://simpleicons.org/icons/'

    # Crear el directorio si no existe
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for name in icon_names:
        icon_url = f'{base_url}{name.lower()}.svg'
        response = requests.get(icon_url)

        if response.status_code == 200:
            file_path = os.path.join(download_dir, f'{name}.svg')
            with open(file_path, 'wb') as file:
                file.write(response.content)
            print(f'Descargado: {name}')
        else:
            print(f'No se pudo descargar el ícono: {name}')


# Lista de nombres de íconos que deseas descargar
icon_names = [
    "JavaScript",
    "Python",
    "Java",
    "MySQL",
    "NodeJS",
    "HTML",
    "CSS",
    "React",
    "Angular",
    "Docker",
    "Ruby",
    "PHP",
    "Kotlin",
    "Swift",
    "TypeScript",
    "Go",
    "Rust",
    "SQL",
    "PostgreSQL",
    "MongoDB",
    "C#",
    "C++",
    "VueJS",
    "SASS",
    "LESS",
    "Bootstrap",
    "jQuery",
    "Laravel",
    "Django",
    "Flask",
    "Spring",
    "ASP.NET",
    "Rails",
    "GraphQL",
    "Elixir",
    "Haskell",
    "Scala",
    "Perl",
    "TensorFlow",
    "PyTorch",
    "Keras",
    "Redis",
    "GraphQL",
    "Electron",
    "AWS",
    "Azure",
    "GCP",
    "Kubernetes",
    "Terraform",
    "Ansible",
    "Puppet",
    "Chef",
    "Hadoop",
    "Spark",
    "Hive",
    "Kafka",
    "Tableau",
    "PowerBI",
    "MATLAB",
    "R",
    "Julia",
    "Apache",
    "Nginx",
    "Tomcat",
    "IIS",
    "Webpack",
    "Gulp",
    "Grunt",
    "Babel",
    "ESLint",
    "Prettier",
    "Jest",
    "Mocha",
    "Chai",
    "Jenkins",
    "TravisCI",
    "CircleCI",
    "Git",
    "SVN",
    "Mercurial",
    "Bitbucket",
    "GitHub",
    "GitLab",
    "Firebase",
    "Realm",
    "Supabase",
    "Netlify",
    "Heroku"
]


# Llamada a la función para descargar los íconos
download_icons(icon_names)
