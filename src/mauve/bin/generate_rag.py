import uuid
import argparse

from mauve.rag.model import RAGModel


def main():  # pragma: nocover

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name',
        type=str,
        dest='name',
        default=str(uuid.uuid4())
    )
    parser.add_argument(
        '--includes',
        type=str,
        dest='includes',
        default=None
    )
    parser.add_argument(
        '--max-lines',
        type=int,
        dest='max_lines',
        default=50000
    )
    parser.add_argument(
        '--regenerate',
        type=bool,
        dest='regenerate',
        action='store_true'
    )
    parser.add_argument(
        '--question',
        type=int,
        dest='question',
        default=None
    )
    args = parser.parse_args()

    model = RAGModel(
        args.name,
        includes=args.includes,
        max_lines=args.max_lines
    )
    model.load(regenerate=args.regenerate)
    if args.question:
        print(model.ask(args.question))


if __name__ == '__main__':  # pragma: nocover
    main()
