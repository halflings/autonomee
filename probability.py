from math import cos, sin, exp, pi, sqrt
import random
import svg

FORWARD_NOISE = 0.05
TURN_NOISE = 0.05
SENSE_NOISE = 0.05

def Gaussian(mu, sigma, x):
    # calculates the probability of x for 1-dim Gaussian with mean mu and var. sigma
    return exp(- ((mu - x) ** 2) / (sigma ** 2) / 2.0) / sqrt(2.0 * pi * (sigma ** 2))

class ParticleFilter(object):

    def __init__(self, map, objectAngle, numParticles = 100):
        self.map = map
        self.width = map.width
        self.height = map.height

        self.particles = set()

        for i in xrange(numParticles):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)

            while map.isObstacle(x, y):
                x = random.randint(0, self.width)
                y = random.randint(0, self.height)

            self.particles.add( Particle(x, y, angle = objectAngle, probability = 1. ) ) # / numParticles  )

    def sense(self, measuredDistance, angle):

        for particle in self.particles:
            particleDist = self.map.rayDistance( particle.x, particle.y, angle )

            # TODO : What should we do for particleDist == None ? ( eg: infinite distance => no object ahead )
            if particleDist is None:
                particleDist = self.width + self.height # Majoration ...

            particle.p *= Gaussian(particleDist, SENSE_NOISE, measuredDistance)

    def move(self, distance, angle = 0.):

        for particle in self.particles:

            # We update the particle's orientation
            deltaAngle = angle + random.gauss(0.0, TURN_NOISE)
            particle.turnAngle(deltaAngle)
            # ...  and it's position
            deltaDistance = distance + random.gauss(0.0, FORWARD_NOISE)
            particle.move(deltaDistance)

            # If the particle got out of the universe, we put it on the border
            particle.x = min( max(0, particle.x) , self.width )
            particle.y = min( max(0, particle.y) , self.height )


    def resample(self):

        # We normalize the particle's weights (probability)
        sumProba = sum( particle.p for particle in self.particles )
        for particle in self.particles:
            particle.p /= sumProba

        # Resampling (resampling wheel algorithm, cf Udacity)
        newParticles = set()
        maxProba = max( particle.p for particle in self.particles )
        index = random.randint(0, len(self.particles))
        B = 0.0

        for i in xrange( len(self.particles) ):
            B += random.randint(0, int(2 * maxProba))

            while self.particles[index].p < B:
                B -= self.particles[index].p
                index = (index + 1) % len(self.particles)

            newParticles.add( self.particles[index] )

        self.particles = newParticles


    def __repr__(self):
        repr = ""
        for particle in self.particles:
            repr += particle.__repr__() + '\n'

        return repr


class Particle(object):

    def __init__(self, x, y, angle = 0., probability = 0.):

        self.x, self.y = x, y
        self.angle = angle
        self.p = probability

    def turnAngle(self, deltaAngle):

        self.angle = (self.angle + deltaAngle + pi) % (2*pi) - pi

    def move(self, displacement):

        dx = displacement * cos(self.angle)
        dy = - displacement * sin(self.angle)

        self.x, self.y = int(self.x + dx) , int(self.y + dy)

    def __repr__(self):
        return '[x={} y={} orient={} | proba={}]'.format(self.x, self.y, self.angle, self.p)


if __name__ == "__main__":

    myMap = svg.SvgTree("maps/mapexample.svg")

    proba = ParticleFilter(myMap, 0)

    proba.move(10, 0)

    proba.sense(10, 0)

    print proba
