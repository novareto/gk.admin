from setuptools import setup, find_packages
import os


long_description = ""

test_requires = [
    ]

setup(name='gk.admin',
      version='0.4.dev0',
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
          'uvc.themes.btwidgets',
          'barrel',
          'cromlech.dawnlight',
          'cromlech.i18n',
          'cromlech.security',
          'cromlech.webob',
          'dolmen.sqlcontainer',
          'sqlalchemy',
          'transaction',
          'ul.auth',
          'uvclight',
          'zope.i18nmessageid',
          'zope.interface',
          'zope.location',
          'zope.schema',
          'setuptools',
        ],
      entry_points={
         'paste.app_factory': [
             'app = gk.admin:admin',
         ],
        'paste.filter_app_factory': [
            'messages = gk.admin:messages_injector',
        ]
      }
      )
