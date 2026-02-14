from infrastructure.ui.tkinter.app import SearchApp
from infrastructure.external.file_repository import LocalFileRepository
from use_cases.search_files import SearchFilesUseCase
from use_cases.benchmark import BenchmarkUseCase
from use_cases.estimation import EstimationUseCase
from adapters.controllers.search_controller import SearchController

def main():
    # Setup dependencies
    file_repo = LocalFileRepository()

    # Setup use cases
    search_use_case = SearchFilesUseCase(file_repo)
    benchmark_use_case = BenchmarkUseCase()
    estimation_use_case = EstimationUseCase()

    # Setup controller
    controller = SearchController(search_use_case, benchmark_use_case, estimation_use_case)

    # Start UI
    app = SearchApp(controller)
    app.mainloop()

if __name__ == "__main__":
    main()
