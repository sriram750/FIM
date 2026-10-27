"""
Builds a 100% valid Windows Installer (.msi) database for FIM Enterprise Agent
using the native Windows Installer engine (msilib / OLE Structured Storage).
"""
import msilib
import msilib.schema
import msilib.sequence
import msilib.text
import os
import sys
import uuid

PRODUCT_NAME = "FIM Enterprise Agent"
MANUFACTURER = "FIM Enterprise Security"
VERSION = "1.0.0"
PRODUCT_CODE = "{88C82F24-B1D6-4F18-9730-C272C15AA801}"
UPGRADE_CODE = "{94F02737-F7E6-4A0B-8902-86A34F90C199}"

def build_msi():
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dist"))
    exe_path = os.path.join(dist_dir, "fim-agent.exe")
    msi_path = os.path.join(dist_dir, "fim-agent-installer.msi")

    if not os.path.exists(exe_path):
        print(f"[!] Target binary not found: {exe_path}")
        sys.exit(1)

    print(f"[*] Packaging {exe_path} into Windows Installer package (.msi)...")

    # If old msi exists, delete it first
    if os.path.exists(msi_path):
        try:
            os.remove(msi_path)
        except Exception as e:
            print(f"[!] Warning deleting old msi: {e}")

    # 1. Initialize MSI database with standard schema
    db = msilib.init_database(
        msi_path,
        msilib.schema,
        PRODUCT_NAME,
        PRODUCT_CODE,
        VERSION,
        MANUFACTURER
    )

    # 2. Add standard actions and sequence tables
    msilib.add_tables(db, msilib.sequence)
    msilib.add_tables(db, msilib.text)

    # 3. Configure Properties
    properties = [
        ("UpgradeCode", UPGRADE_CODE),
        ("ALLUSERS", "1"),
        ("ARPNOMODIFY", "1"),
        ("ARPNOREPAIR", "1"),
        ("ARPPRODUCTICON", "FIMAgentIcon"),
        ("InstallMode", "Typical"),
    ]
    for prop, val in properties:
        view = db.OpenView(f"SELECT `Property`, `Value` FROM `Property` WHERE `Property`='{prop}'")
        view.Execute(None)
        rec = view.Fetch()
        if rec:
            upd = db.OpenView(f"UPDATE `Property` SET `Value`='{val}' WHERE `Property`='{prop}'")
            upd.Execute(None)
        else:
            msilib.add_data(db, "Property", [(prop, val)])

    # 4. Create Cabinet and Root Feature
    cab = msilib.CAB("fim_agent.cab")
    feature = msilib.Feature(
        db,
        "FIMAgentFeature",
        "FIM Enterprise Agent Core",
        "Installs FIM Enterprise endpoint watcher, hasher, and spooler service.",
        1,
        directory="TARGETDIR"
    )

    # 5. Define Directory Hierarchy: TARGETDIR -> ProgramFilesFolder -> FIM Enterprise Agent
    target_dir = msilib.Directory(db, cab, None, dist_dir, "TARGETDIR", "SourceDir")
    prog_files = msilib.Directory(db, cab, target_dir, ".", "ProgramFilesFolder", "PFiles")
    app_dir = msilib.Directory(
        db,
        cab,
        prog_files,
        ".",
        "FIMAGENTDIR",
        "FIMENT~1|FIM Enterprise Agent"
    )

    # 6. Add fim-agent.exe Component & File
    app_dir.start_component(
        "FIMAgentExeComponent",
        feature,
        flags=0,
        keyfile="fim-agent.exe"
    )
    app_dir.add_file("fim-agent.exe", src="fim-agent.exe")

    # 7. Commit Cabinet (FCICreate) and database
    print("[*] Generating embedded cabinet stream...")
    cab.commit(db)
    db.Commit()

    size_mb = os.path.getsize(msi_path) / (1024 * 1024)
    print(f"[OK] Successfully built genuine Windows Installer package: {msi_path} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    build_msi()
