!macro preInit
  SetRegView 64

  ClearErrors
  ReadRegStr $0 HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${If} ${Errors} 
    ${OrIf} $0 == ""
      WriteRegExpandStr HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation "C:\SWAT\SWATEditor\SwatCheck"
  ${EndIf}

  ClearErrors
  ReadRegStr $0 HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${If} ${Errors} 
    ${OrIf} $0 == ""
      WriteRegExpandStr HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation "C:\SWAT\SWATEditor\SwatCheck"
  ${EndIf}
!macroend