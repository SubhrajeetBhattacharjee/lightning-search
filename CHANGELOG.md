# Changelog

All notable changes to Lightning Search will be documented here.

## [1.0.0] - 2026-01-XX

### Added
- Initial release
- Code indexing with Tree-sitter parser
- Fast search (sub-millisecond queries)
- Control Flow Graph analysis
- Cyclomatic complexity calculation
- Interactive search mode
- CLI with 5 commands
- Tested on 651k lines of code

### Performance
- 436 files/sec indexing rate
- 0.03-0.25ms search times
- 16-21x compression ratio
- Scales linearly to 651k lines

### Tested On
- Flask (18k lines)
- Django (508k lines)
- pandas (651k lines)