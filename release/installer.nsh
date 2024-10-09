!macro preInit
  SetRegView 64

  ClearErrors
  ReadRegStr $0 HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${If} ${Errors} 
    ${OrIf} $0 == ""
	  WriteRegExpandStr HKLM "${INSTALL_REGISTRY_KEY}" InstallLocation "C:\SWAT\SWATPlus\SWATPlusEditor"
  ${EndIf}

  ClearErrors
  ReadRegStr $0 HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation
  ${If} ${Errors} 
    ${OrIf} $0 == ""      
	  WriteRegExpandStr HKCU "${INSTALL_REGISTRY_KEY}" InstallLocation "$PROFILE\SWATPlus\SWATPlusEditor"
  ${EndIf}
!macroend

!macro customInstall
  SetOutPath "$INSTDIR\..\Databases"
  File "${BUILD_RESOURCES_DIR}\swatplus_datasets.sqlite"
!macroend

!macro customRemoveFiles
  Delete "$INSTDIR\..\Databases\swatplus_datasets.sqlite"
  RMDir /r $INSTDIR
!macroend