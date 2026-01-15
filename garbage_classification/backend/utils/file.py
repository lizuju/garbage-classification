import os
from pathlib import Path


def allowed_file(filename: str, allowed_exts) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts


def resolve_stored_path(stored_path: str, project_root: Path, backend_dir: Path):
    """
    兼容历史数据/不同启动目录造成的路径差异：
    - 数据库里可能存了相对路径 uploads/...
    - 或存了 backend/uploads/... 的绝对路径
    - 实际文件可能在 <项目根>/uploads/...
    返回：存在的绝对路径字符串；若找不到返回 None
    """
    if not stored_path:
        return None

    p = Path(stored_path)
    candidates = [p]

    if not p.is_absolute():
        candidates.append(project_root / p)
        candidates.append(backend_dir / p)

    # backend/uploads -> <root>/uploads 映射
    try:
        backend_uploads = (backend_dir / 'uploads').resolve()
        root_uploads = (project_root / 'uploads').resolve()
        if str(backend_uploads) in str(p):
            candidates.append(Path(str(p).replace(str(backend_uploads), str(root_uploads))))
    except Exception:
        pass

    for c in candidates:
        try:
            cp = c.resolve() if not c.is_absolute() else c
            if cp.exists():
                return str(cp)
        except Exception:
            continue
    return None

