project('neomir-plugins',
  version: '1.0.0',
  meson_version: '>= 0.60.0'
)

# Get base system directory via get_option
plugins_install_dir = get_option('datadir') / 'neomir' / 'plugins'

install_data(
  'example/plugin.json',
  install_dir: plugins_install_dir / 'example',
  install_mode: 'rw-r--r--',
)

install_data(
  'example/example_plugin.py',
  install_dir: plugins_install_dir / 'example',
  install_mode: 'rwxr-xr-x',
)

# Packaging .plug installation archives using tar utility
tar_prog = find_program('tar', required: false)

if tar_prog.found()
  custom_target('example-plug-package',
    input: [
      'example/plugin.json',
      'example/example_plugin.py',
    ],
    output: 'example.plug',
    command: [
      tar_prog,
      '-czf',
      '@OUTPUT@',
      '-C', meson.current_source_dir() / 'example',
      'plugin.json',
      'example_plugin.py',
    ],
    build_by_default: true,
    install: true,
    install_dir: plugins_install_dir,
  )
endif
