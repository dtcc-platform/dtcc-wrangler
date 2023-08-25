set(BINDINGS _dtcc_wrangler)


pybind11_add_module(${BINDINGS} dtcc_wrangler.cpp)

target_compile_definitions(${BINDINGS} PRIVATE -DTRILIBRARY -DANSI_DECLARATORS)
if(WIN32)
    target_compile_definitions(${BINDINGS} PRIVATE -DNO_TIMER)
endif()


install(TARGETS ${BINDINGS} DESTINATION dtcc_wrangler)