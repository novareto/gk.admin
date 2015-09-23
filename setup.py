from setuptools import setup, find_packages
import os

readme_filename = os.path.join('src', 'gk', 'admin', 'README.txt')
long_description = open(readme_filename).read() + '\n\n' + \
                   open('CHANGES.txt').read()

test_requires = [
    ]

setup(name='gk.admin',
      version='1.0',
      description="Admin system for Gatekeeper",
      long_description = long_description,
      classifiers=['Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Zope Public License',
                   'Programming Language :: Python',
                   'Framework :: Zope3',
                   ],
      keywords='admin gatekeeper',
      author='Novareto',
      author_email='grok-dev@zope.org',
      url='http://grok.zope.org',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['gk'],
      include_package_data=True,
      zip_safe=False,
      extras_require={'test': test_requires},
      install_requires=[
        "uvc.themes.btwidgets",
        ],
      )
