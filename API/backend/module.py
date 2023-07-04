# Library Imports
import API.lock as lock
import pathlib

# Local Imports
from .utils import get_backend_endpoint, get_jwt, RequestAutoRefresh

# Keeps the status of modules, can be imported to get the status
class ModuleStatus:
    INIT    = 'INIT'
    LOADING = 'LOADING'
    COMPLETE= 'COMPLETE'
    STOP    = 'STOP'
    ERROR   = 'ERROR'

# An API that helps with storing results of modules. Due to the unique nature of the JSON.
# Changes have to be forced.
class ModuleResult(lock.LockSection):
    # Force serialize changes
    def serialize_changes(self) -> dict:
        return self.serialize()
    # Converts module result paths into shared paths from work paths
    def convert_to_shared(self, work_dir : pathlib.Path, share_dir : pathlib.Path):
        set_dict    = {}
        for k, v in self._fields.items():
            if v._type == pathlib.Path and work_dir in v.get().parents:
                set_dict[k] = share_dir / v.get().relative_to(work_dir)
        self.set(**set_dict)
    # Converts module result paths into work paths from shared_paths
    def convert_to_work(self, work_dir : pathlib.Path, share_dir : pathlib.Path):
        set_dict    = {}
        for k, v in self._fields.items():
            if v._type == pathlib.Path and share_dir in v.get().parents:
                set_dict[k] = work_dir / v.get().relative_to(share_dir)
        self.set(**set_dict)
    # Create symlnks
    # This function automatically deletes previous datas. 
    # Use this function only if this function is your only manager. Otherwise, override
    def create_symlnk(self, work_dir : pathlib.Path, share_dir : pathlib.Path):
        def _create_symlnk_ignore_errors(src : pathlib.Path, target : pathlib.Path):
            # Create directories before starting
            if not target.parent.exists():
                target.parent.mkdir(0o777, True, True)
            # Remove previous datas before linking
            if target.is_symlink(): target.unlink()
            elif target.is_file(): target.unlink()
            elif target.is_dir(): target.rmdir()
            target.symlink_to(src)

        for k, v in self._fields.items():
            if v._type == pathlib.Path and share_dir in v.get().parents:
                share_path  = v.get()
                work_path   = work_dir / share_path.relative_to(share_dir)

            elif v._type == pathlib.Path and work_dir in v.get().parents:
                work_path   = v.get()
                share_path  = share_dir / work_path.relative_to(work_dir)
            _create_symlnk_ignore_errors(work_path, share_path)


# Module Section for Auto Refreshing
class ModuleSection(RequestAutoRefresh):
    status      = lock.LockField(str, ModuleStatus.INIT)
    progress    = lock.LockField(float, 0)
    result_avail= lock.LockField(bool, False)
    allow_cont  = lock.LockField(bool, False)
    has_warning = lock.LockField(bool, False)
    lock        = lock.LockField(bool, False)
    results     = ModuleResult()


# Wraps Module Section 
class Module:
    MODULE_ENDPOINT = 'bio/module/{module_id}/'
    MODULE_SECTION  = ModuleSection
    def __init__(self, module_id : int):
        endpoint    = get_backend_endpoint()
        endpoint    = endpoint + self.MODULE_ENDPOINT.format(
            module_id = module_id
        )
        jwt         = get_jwt()
        self._module = self.MODULE_SECTION(
            endpoint = endpoint, header = {'Authorization' : f'Token {jwt}'}
        )
    def module(self) -> ModuleSection:
        return self._module