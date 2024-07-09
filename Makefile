#
# Makefile (LatticeConvert)
#

all:
	install convert-lattice.py ${WORKLOCAL}/local/bin/

	install ElegantParser.py ${WORKLOCAL}/local/python/
	install LatticeConvert.py ${WORKLOCAL}/local/python/
	install LatticeData.py ${WORKLOCAL}/local/python/
	install LatticeParser.py ${WORKLOCAL}/local/python/
	install MADXParser.py ${WORKLOCAL}/local/python/
	install SixDSimParser.py ${WORKLOCAL}/local/python/

clean:
	rm -f ${WORKLOCAL}/local/bin/convert-lattice.py

	rm -f ${WORKLOCAL}/local/python/ElegantParser.py
	rm -f ${WORKLOCAL}/local/python/LatticeConvert.py
	rm -f ${WORKLOCAL}/local/python/LatticeData.py
	rm -f ${WORKLOCAL}/local/python/LatticeParser.py
	rm -f ${WORKLOCAL}/local/python/MADXParser.py
	rm -f ${WORKLOCAL}/local/python/SixDSimParser.py
