Option Explicit
Dim shell, fso, root, pythonw
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = fso.GetParentFolderName(WScript.ScriptFullName)
If fso.FileExists(fso.BuildPath(root, "CyAICodex.exe")) Then
  shell.CurrentDirectory = root
  shell.Run Chr(34) & fso.BuildPath(root, "CyAICodex.exe") & Chr(34), 0, False
  WScript.Quit 0
End If
pythonw = fso.BuildPath(root, ".venv\Scripts\pythonw.exe")
If Not fso.FileExists(pythonw) Then
  MsgBox "Lancez Installer.ps1 une premiere fois pour preparer l'application.", 48, "CyAICodex"
  WScript.Quit 1
End If
shell.CurrentDirectory = root
shell.Run Chr(34) & pythonw & Chr(34) & " " & Chr(34) & fso.BuildPath(root, "run.py") & Chr(34), 0, False
