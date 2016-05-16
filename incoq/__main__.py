"""Alias for incoq.compiler's entry point."""


if __name__ == '__main__':
    import sys
    import incoq.compiler.__main__ as main
    main.run(sys.argv[1:])
